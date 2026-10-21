"""Deterministic RC room fixture; synthetic results are not commissioning evidence."""

import math
from dataclasses import asdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from zone_controller.control.sequence import Controller
from zone_controller.points import Reading


def run(database: dict, schedule: dict, days: int = 7) -> dict:
    if not 1 <= days <= 365:
        raise ValueError("Simulation duration must be 1..365 days")
    controller = Controller(database, schedule)
    start = datetime(2026, 10, 19, tzinfo=ZoneInfo(schedule["timezone"]))
    zone = 23.0
    samples = []
    fan_edges = []
    previous_fan = False
    dt = 30
    for now in range(0, days * 86400, dt):
        when = start + timedelta(seconds=now)
        outdoor = 22 + 4 * math.sin(2 * math.pi * (when.hour - 8) / 24)
        inputs = {
            name: Reading(value, now)
            for name, value in {
                "ZN-T": zone,
                "SA-T": 22.0,
                "ZN-CO2": 850.0,
                "OCC-COUNT": 1 if 8 <= when.hour < 18 else 0,
            }.items()
        }
        output = controller.tick(float(now), when, inputs)
        if output.fan != previous_fan:
            fan_edges.append({"time_s": now, "fan": output.fan})
        previous_fan = output.fan
        # Lumped RC leakage plus an idealized transfer fan to a temperate downstairs.
        # A real booster can heat or cool only if source air permits it.
        zone += dt * ((outdoor - zone) / 21600 + (22.5 - zone) / 1800 * output.fan)
        if now % 300 == 0:
            samples.append({"time": when.isoformat(), "zone_c": round(zone, 4), **asdict(output)})
    return {
        "synthetic": True,
        "days": days,
        "step_s": dt,
        "model": "RC room with idealized downstairs air transfer; not a building prediction",
        "fan_runtime_h": round(controller.fan_runtime_s / 3600, 3),
        "fan_edges": fan_edges,
        "transitions": controller.transitions,
        "samples": samples,
    }
