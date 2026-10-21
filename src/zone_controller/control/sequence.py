"""Pure sequence model. No hardware output or network side effects."""

import logging
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from zone_controller.points import PriorityArray, Reading, validate_setpoints

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Output:
    mode: str
    heat: float
    cool: float
    fan: bool
    damper: float
    alarms: tuple[str, ...]
    reason: str


class Controller:
    def __init__(self, database: dict, schedule: dict):
        self.db = database
        self.cfg = database["control"]
        self.schedule = schedule
        self.fan_command = PriorityArray(False)
        self.setpoints = {
            name: PriorityArray(p["bacnet"]["relinquish_default"])
            for name, p in database["points"].items()
            if "-SP-" in name
        }
        self.mode = "Unoccupied"
        self.fan = False
        self.last_change = 0.0
        self.last_tick = None
        self.empty_since = None
        self.trim_at = None
        self.damper = 0.0
        self.fan_runtime_s = 0.0
        self.transitions = []

    def write_setpoint(self, name: str, value: float | None, priority: int = 8):
        slot = self.setpoints[name]
        previous = list(slot.slots)
        slot.write(priority, value)
        try:
            for suffix in ("OCC", "STBY", "UNOCC"):
                validate_setpoints(
                    self.setpoints[f"HTG-SP-{suffix}"].value,
                    self.setpoints[f"CLG-SP-{suffix}"].value,
                    self.cfg["deadband_c"],
                )
        except (ValueError, TypeError):
            slot.slots = previous
            raise ValueError("Setpoint write rejected by deadband interlock") from None

    def _schedule(self, when: datetime):
        local = when.astimezone(ZoneInfo(self.schedule["timezone"]))
        period = self.schedule["occupied"]["weekdays" if local.weekday() < 5 else "weekends"]
        start = sum(int(x) * m for x, m in zip(period["start"].split(":"), [3600, 60]))
        end = sum(int(x) * m for x, m in zip(period["end"].split(":"), [3600, 60]))
        sec = local.hour * 3600 + local.minute * 60 + local.second
        return start <= sec < end, start - self.cfg["warmup_before_s"] <= sec < start

    def tick(self, now: float, when: datetime, inputs: dict[str, Reading]) -> Output:
        if when.tzinfo is None:
            raise ValueError("Schedule timestamp must be timezone-aware")
        if now < 0 or (self.last_tick is not None and now < self.last_tick):
            raise ValueError("Controller time must be monotonic and nonnegative")
        if self.last_tick is not None and self.fan:
            self.fan_runtime_s += now - self.last_tick
        self.last_tick = now
        cfg = self.cfg

        def good(name):
            return name in inputs and inputs[name].valid(
                now, self.db["points"][name]["alarm"]["stale_s"]
            )

        scheduled, warmup = self._schedule(when)
        if not scheduled or not good("OCC-COUNT") or inputs["OCC-COUNT"].value > 0:
            self.empty_since = None
        elif self.empty_since is None:
            self.empty_since = now
        if scheduled:
            standby = (
                self.empty_since is not None and now - self.empty_since >= cfg["standby_after_s"]
            )
            mode = "Standby" if standby else "Occupied"
            reason = "sustained zero occupancy" if standby else "occupied schedule"
        else:
            mode = "Warm-up" if warmup else "Unoccupied"
            reason = "pre-occupancy period" if warmup else "outside occupied schedule"
        if mode != self.mode:
            self.transitions.append((now, self.mode, mode, reason))
            log.info("mode %s -> %s: %s", self.mode, mode, reason)
        self.mode = mode
        suffix = {"Occupied": "OCC", "Standby": "STBY", "Unoccupied": "UNOCC", "Warm-up": "OCC"}[
            mode
        ]
        heat = self.setpoints[f"HTG-SP-{suffix}"].value
        cool = self.setpoints[f"CLG-SP-{suffix}"].value
        alarms = [
            f"{name}:fault-or-stale"
            for name in ("ZN-T", "SA-T", "ZN-CO2", "OCC-COUNT")
            if not good(name)
        ]
        unsafe = not good("ZN-T") or not good("SA-T")
        if good("SA-T") and inputs["SA-T"].value > cfg["supply_high_c"]:
            alarms.append("SA-T:high-limit")
            unsafe = True
        if unsafe:
            self.fan_command.write(1, False)
            self.damper = 0.0
        else:
            self.fan_command.write(1, None)
            zone = inputs["ZN-T"].value
            demand = (
                zone < heat - cfg["fan_start_delta_c"] or zone > cool + cfg["fan_start_delta_c"]
            )
            in_band = heat <= zone <= cool
            request = self.fan
            if not self.fan and demand:
                request = True
            elif self.fan and in_band:
                request = False
            self.fan_command.write(16, request)
            if self.trim_at is None or now - self.trim_at >= cfg["trim_interval_s"]:
                change = (
                    cfg["respond_percent"]
                    if zone > cool + cfg["fan_start_delta_c"]
                    else -cfg["trim_percent"]
                )
                self.damper = max(0.0, min(cfg["output_max_percent"], self.damper + change))
                self.trim_at = now
            if not good("ZN-CO2"):
                self.damper = cfg["vent_min_percent"]
            elif inputs["ZN-CO2"].value > cfg["co2_max_ppm"]:
                self.damper = cfg["output_max_percent"]
            elif inputs["ZN-CO2"].value > cfg["co2_min_ppm"]:
                self.damper = max(self.damper, cfg["vent_min_percent"])
        desired = bool(self.fan_command.value)
        dwell = cfg["fan_min_on_s"] if self.fan else cfg["fan_min_off_s"]
        if desired != self.fan and (unsafe or now - self.last_change >= dwell):
            self.fan = desired
            self.last_change = now
        return Output(mode, heat, cool, self.fan, self.damper, tuple(alarms), reason)
