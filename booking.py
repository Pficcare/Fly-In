from dataclasses import dataclass
from parser import Map



@dataclass(frozen=True)
class Step:
    turn: int
    zone: str | None
    link: frozenset[str] | None
    move: str



class Clock:
    def __init__(self, path:list[str], map_info: Map) -> None:
        self.path = path
        self.map_info = map_info
        self.link_capacity: dict[frozenset[str], int] = (
            self.gen_link_capacity()
        )
        self.zone_booked: dict[tuple[str, int], int] = {}
        self.link_booked:  dict[tuple[frozenset[str], int], int] = {}
        self.result: list[list[str]] = []

    def gen_link_capacity(self) -> dict[frozenset[str], int]:
        link_capacity: dict[frozenset[str], int] = {}

        for i in range(len(self.path) - 1):
            curr_zone = self.path[i]
            next_zone = self.path[i + 1]
            key = frozenset({curr_zone, next_zone})
            capacity = self.map_info.connections[curr_zone][next_zone]
            link_capacity[key] = capacity
        return link_capacity

    def itinerary(self, start_turn: int) -> list[Step]:
        steps: list[Step] = []
        turn = start_turn

        for i in range(len(self.path) - 1):
            curr_zone = self.path[i]
            next_zone = self.path[i + 1]
            link = frozenset({curr_zone, next_zone})
            if self.map_info.nodes[next_zone].zone_status == "restricted":
                steps.append(
                    Step(turn + 1, None, link, f"{curr_zone}-{next_zone}")
                )
                steps.append(Step(turn + 2, next_zone, None, next_zone))
                turn += 2
            else:
                steps.append(Step(turn + 1, next_zone, link, next_zone))
                turn += 1
        return steps

    def valid_step(self, steps: list[Step]) -> bool:
        for step in steps:
            if step.zone is not None:
                limit = self.map_info.nodes[step.zone].max_drones
                booked = self.zone_booked.get((step.zone, step.turn), 0)
                if limit is not None and booked >= limit:
                    return False
            if step.link is not None:
                limit = self.link_capacity[step.link]
                booked = self.link_booked.get((step.link, step.turn), 0)
                if booked >= limit:
                    return False
        return True

    def book(self, steps: list[Step], drone_id: int) -> None:
        for step in steps:
            if step.zone is not None:
                zone_key = (step.zone, step.turn)
                booked = self.zone_booked.get(zone_key, 0)
                self.zone_booked[zone_key] = booked + 1
            if step.link is not None:
                link_key = (step.link, step.turn)
                booked = self.link_booked.get(link_key, 0)
                self.link_booked[link_key] = booked + 1
            while len(self.result) < step.turn:
                self.result.append([])
            self.result[step.turn - 1].append(f"D{drone_id}-{step.move}")

