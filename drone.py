from parser import Map
from zone import ZONE_INFO, Zone

# @dataclass
# class Map:  # Regroupe les donnees pour dijka
#     nodes: dict[str, Zone]
#     connections: dict[str, dict[str, int]]
#     map_drone_lmt: int
#     start: Zone
#     end: Zone

# @dataclass(frozen=True)
# class ZoneRestriction:
#     cost: int
#     access: bool
#     priority: bool
#
#
# @dataclass(frozen=True)
# class Zone:
#     name: str
#     coordo: tuple[int, int]
#     zone_status: str = "normal"
#     color: str | None = None
#     max_drones: int | None = 1
#
#
# ZONE_INFO: dict[str, ZoneRestriction] = {
#     "normal": ZoneRestriction(1, True, False),
#     "priority": ZoneRestriction(1, True, True),
#     "restricted": ZoneRestriction(2, True, False),
#     "blocked": ZoneRestriction(1, False, False),


# Creation de la class Drone et de sa logic


class Drone:
    def __init__(self, drone_id: int, drone_path: list[Zone]) -> None:
        self._drone_id: int = drone_id
        self.drone_path = drone_path
        self.flyin: bool = False
        self.move_cost: int = self.path_cost()
        self.index: int = 0

    @property
    def drone_id(self) -> int:
        return self._drone_id

    def update_position(self) -> None:
        if self.index < len(self.drone_path) - 1:
            self.index += 1
            self.move_cost -= ZONE_INFO[self.drone_path[self.index].zone_status].cost
        else:
            raise ValueError

    def return_position(self) -> str:
        return self.drone_path[self.index].name

    def path_cost(self) -> int:
        cost: int = 0

        for i in range(1, len(self.drone_path)):
            cost += ZONE_INFO[self.drone_path[i].zone_status].cost
        return cost

    def switch_mode(self) -> None:
        if not self.flyin:
            self.flyin = True
        else:
            self.flyin = False

    def reach_the_end(self) -> bool:
        return self.index == len(self.drone_path) - 1

    def key_tuple(self) -> tuple[bool, int, int]:
        return (not self.flyin, self.move_cost, self._drone_id)


class ZoneState:
    def __init__(self, curr_zone: Zone) -> None:
        self.capacity = curr_zone.max_drones

    def free_spot(self) -> bool:
        return True if self.capacity is None or self.capacity > 0 else False

    def add_slot(self) -> None:
        if self.capacity is not None:
            self.capacity += 1

    def del_slot(self) -> None:
        if self.capacity is not None:
            self.capacity -= 1


class LinkZone:
    def __init__(self, link_capacity: int) -> None:
        self.capacity = link_capacity

    def free_spot(self) -> bool:
        return self.capacity > 0

    def add_slot(self) -> None:
        self.capacity += 1

    def del_slot(self) -> None:
        self.capacity -= 1


class Engine:
    def __init__(self, path: list[str], map_info: Map) -> None:
        self.path = path
        self.map_info = map_info
        self.drone_list: list[Drone] = self.gen_drones()
        self.zone_state: dict[str, ZoneState] = self.gen_zone_state()
        self.links: dict[frozenset[str], LinkZone] = self.gen_links()
        self.backup: list[list[str]] = []

    def gen_drones(self) -> list[Drone]:
        drone_list: list[Drone] = []
        drone_path: list[Zone] = (
            self.gen_path()
        )  # Give the path and data from each Zone to each drones

        for i in range(1, self.map_info.map_drone_lmt + 1):
            drone_list.append(Drone(i, drone_path))
        return drone_list

    def gen_path(self) -> list[Zone]:
        path_list: list[Zone] = []

        for el in self.path:
            path_list.append(self.map_info.nodes[el])
        return path_list

    def gen_links(self) -> dict[frozenset[str], LinkZone]:
        links: dict[frozenset[str], LinkZone] = {}

        for node, nbors in self.map_info.connections.items():
            for nbor, link_capacity in nbors.items():
                key = frozenset({node, nbor})
                if key not in links:
                    links[key] = LinkZone(link_capacity)
        return links

    def gen_zone_state(self) -> dict[str, ZoneState]:
        state: dict[str, ZoneState] = {}

        for key, el in self.map_info.nodes.items():
            state[key] = ZoneState(el)
        return state

    def not_all_arrived(self) -> bool:

        for el in self.drone_list:
            if not el.reach_the_end():
                return True
        return False

    def engine_v12_biturbo(self) -> None:

        while self.not_all_arrived():
            moves: list[str] = []
            links_used: list[frozenset] = []
            drones_sorted = sorted(self.drone_list, key=Drone.key_tuple)

            for drone in drones_sorted:
                if drone.reach_the_end():
                    continue
                if drone.flyin:
                    drone.switch_mode()
                    link_to_free = frozenset(
                        {
                            drone.return_position(),
                            drone.drone_path[drone.index + 1].name,
                        }
                    )
                    self.links[link_to_free].add_slot()
                    drone.update_position()
                    moves.append(f"D{drone.drone_id}-{drone.return_position()}")
                else:
                    curr_zone = drone.return_position()
                    next_zone = drone.drone_path[drone.index + 1].name
                    link = self.links[frozenset({curr_zone, next_zone})]
                    if link.free_spot() and self.zone_state[next_zone].free_spot():
                        if (
                            drone.drone_path[drone.index + 1].zone_status
                            == "restricted"
                        ):
                            drone.switch_mode()
                            self.zone_state[curr_zone].add_slot()
                            self.zone_state[next_zone].del_slot()
                            link.del_slot()
                            moves.append(f"D{drone.drone_id}-{curr_zone}-{next_zone}")
                        else:
                            self.zone_state[curr_zone].add_slot()
                            self.zone_state[next_zone].del_slot()
                            link.del_slot()
                            drone.update_position()
                            links_used.append(frozenset({curr_zone, next_zone}))
                            moves.append(f"D{drone.drone_id}-{drone.return_position()}")
                    else:
                        continue
            for el in links_used:
                self.links[el].add_slot()

            if not moves:
                raise ValueError  # to change by custome error

            self.backup.append(moves)

    def print_backup(self) -> None:
        for el in self.backup:
            line = " ".join(el)
            print(line)
            

