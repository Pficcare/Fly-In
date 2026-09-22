from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneRestriction:
    cost: int
    access: bool
    priority: bool


ZONE_INFO: dict[str, ZoneRestriction] = {
    "normal": ZoneRestriction(1, True, False),
    "priority": ZoneRestriction(1, True, True),
    "restricted": ZoneRestriction(2, True, False),
    "blocked": ZoneRestriction(1, False, False),
} # Data du dic ne sont pas frozen
