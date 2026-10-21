"""Driver contract: return quality, never silently reuse a stale measurement."""

from typing import Protocol

from zone_controller.points import Reading


class InputDriver(Protocol):
    def read(self, now: float) -> Reading: ...
