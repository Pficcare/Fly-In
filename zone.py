from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneRestriction:
    cost: int
    access: bool
    priority: bool


@dataclass(frozen=True)
class Zone:
    name: str
    coordo: tuple[int, int]
    zone_status: str = "normal"
    color: str | None = None
    max_drones: int | None = 1


ZONE_INFO: dict[str, ZoneRestriction] = {
    "normal": ZoneRestriction(1, True, False),
    "priority": ZoneRestriction(1, True, True),
    "restricted": ZoneRestriction(2, True, False),
    "blocked": ZoneRestriction(1, False, False),
} # Data du dic ne sont pas frozen
