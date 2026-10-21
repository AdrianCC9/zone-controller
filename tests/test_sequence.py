from datetime import datetime
from itertools import pairwise
from zoneinfo import ZoneInfo

import pytest

from zone_controller.points import PriorityArray, Quality, Reading
from zone_controller.simulation import run


def when(hour=10, minute=0, day=19):
    return datetime(2026, 10, day, hour, minute, tzinfo=ZoneInfo("America/Toronto"))


def readings(now, zone=27, supply=25, co2=800, occupancy=1):
    return {
        name: Reading(value, now)
        for name, value in {
            "ZN-T": zone,
            "SA-T": supply,
            "ZN-CO2": co2,
            "OCC-COUNT": occupancy,
        }.items()
    }


def test_priority_override_and_relinquish():
    p = PriorityArray(False)
    p.write(16, True)
    p.write(8, False)
    assert p.value is False
    p.write(8, None)
    assert p.value is True
    p.write(16, None)
    assert p.value is False


@pytest.mark.parametrize("priority", [0, 17, True, 1.5])
def test_priority_rejects_bad_slots(priority):
    with pytest.raises(ValueError):
        PriorityArray(False).write(priority, True)


def test_setpoint_write_rolls_back(controller):
    with pytest.raises(ValueError):
        controller.write_setpoint("HTG-SP-OCC", 25.0)
    assert controller.setpoints["HTG-SP-OCC"].value == 21.5
    controller.write_setpoint("HTG-SP-OCC", 22.0)
    assert controller.tick(0, when(), readings(0)).heat == 22.0


def test_fan_minimum_on_off(controller):
    assert not controller.tick(0, when(), readings(0)).fan
    assert not controller.tick(299, when(), readings(299)).fan
    assert controller.tick(300, when(), readings(300)).fan
    assert controller.tick(899, when(), readings(899, zone=23)).fan
    assert not controller.tick(900, when(), readings(900, zone=23)).fan
    assert not controller.tick(1199, when(), readings(1199)).fan
    assert controller.tick(1200, when(), readings(1200)).fan


def test_high_limit_defeats_override_and_minimum_on(controller):
    controller.fan_command.write(8, True)
    assert controller.tick(300, when(), readings(300)).fan
    out = controller.tick(301, when(), readings(301, supply=51))
    assert not out.fan and out.damper == 0
    assert "SA-T:high-limit" in out.alarms
    assert not controller.tick(302, when(), readings(302)).fan


@pytest.mark.parametrize(
    "bad", [Reading(27, 0), Reading(27, 300, Quality.FAULT), Reading(float("nan"), 300)]
)
def test_bad_zone_fails_safe(controller, bad):
    inputs = readings(300)
    inputs["ZN-T"] = bad
    assert not controller.tick(300, when(), inputs).fan


def test_standby_and_vision_failure_fallback(controller):
    assert controller.tick(0, when(), readings(0, occupancy=0)).mode == "Occupied"
    assert controller.tick(1200, when(), readings(1200, occupancy=0)).mode == "Standby"
    inputs = readings(1201, occupancy=0)
    del inputs["OCC-COUNT"]
    assert controller.tick(1201, when(), inputs).mode == "Occupied"


@pytest.mark.parametrize(
    "hour,minute,day,mode",
    [
        (7, 29, 19, "Unoccupied"),
        (7, 30, 19, "Warm-up"),
        (8, 0, 19, "Occupied"),
        (22, 0, 19, "Unoccupied"),
        (8, 0, 24, "Unoccupied"),
        (9, 0, 24, "Occupied"),
    ],
)
def test_schedule(controller, hour, minute, day, mode):
    assert controller.tick(0, when(hour, minute, day), readings(0)).mode == mode


def test_ventilation_and_trim(controller):
    assert controller.tick(0, when(), readings(0, co2=1100)).damper >= 20
    assert controller.tick(120, when(), readings(120, co2=1500)).damper == 100
    assert controller.tick(240, when(), readings(240, zone=23)).damper == 98


def test_future_reading_is_invalid():
    assert not Reading(20, 301).valid(300, 300)


def test_week_rc_model(database, schedule):
    result = run(database, schedule, 7)
    assert result["synthetic"]
    assert len(result["samples"]) == 7 * 24 * 12
    edges = result["fan_edges"]
    assert edges
    for previous, current in pairwise(edges):
        minimum = 600 if previous["fan"] else 300
        assert current["time_s"] - previous["time_s"] >= minimum
    assert {sample["mode"] for sample in result["samples"]} == {
        "Unoccupied",
        "Occupied",
        "Standby",
        "Warm-up",
    }
    assert all(not sample["alarms"] for sample in result["samples"])
    # Fixture-specific comfort envelope, not proof of field performance.
    assert all(s["heat"] - 1.5 <= s["zone_c"] <= s["cool"] + 1.5 for s in result["samples"])
