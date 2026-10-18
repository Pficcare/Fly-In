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

