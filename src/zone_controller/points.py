"""Point database, quality and protocol-independent priority arbitration."""

import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml


class Quality(str, Enum):
    GOOD = "good"
    FAULT = "fault"


@dataclass(frozen=True)
class Reading:
    value: float | bool
    timestamp: float
    quality: Quality = Quality.GOOD

    def valid(self, now: float, stale_s: float) -> bool:
        age = now - self.timestamp
        return self.quality == Quality.GOOD and 0 <= age < stale_s and math.isfinite(self.value)


def load_database(path: str | Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    seen = set()
    for name, point in data["points"].items():
        obj = point["bacnet"]
        key = (obj["type"], obj["instance"])
        if key in seen:
            raise ValueError(f"Duplicate BACnet identifier at {name}: {key}")
        seen.add(key)
        if not point["haystack"] or point["trend"]["interval_s"] <= 0:
            raise ValueError(f"Invalid tags/trending at {name}")
    for mode in ("OCC", "STBY", "UNOCC"):
        heat = data["points"][f"HTG-SP-{mode}"]["bacnet"]["relinquish_default"]
        cool = data["points"][f"CLG-SP-{mode}"]["bacnet"]["relinquish_default"]
        validate_setpoints(heat, cool, data["control"]["deadband_c"])
    return data


def validate_setpoints(heat: float, cool: float, deadband: float) -> None:
    if not all(math.isfinite(x) for x in (heat, cool, deadband)):
        raise ValueError("Setpoints must be finite")
    if deadband <= 0 or heat > cool - deadband:
        raise ValueError("Heating/cooling setpoints violate the deadband")


class PriorityArray:
    """Sixteen slots; lower priority number wins; None relinquishes a slot.

    This is an internal model, not an implemented BACnet network object.
    """

    def __init__(self, default):
        self.default = default
        self.slots = [None] * 16

    def write(self, priority: int, value) -> None:
        if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 16:
            raise ValueError("Priority must be an integer from 1 to 16")
        self.slots[priority - 1] = value

    @property
    def value(self):
        return next((v for v in self.slots if v is not None), self.default)
