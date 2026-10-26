from errors import SimulationError
from parser import Map
from zone import Zone
from drone import Drone


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
    def __init__(
        self, path: list[str], map_info: Map, depart: dict[int, int]
    ) -> None:
        self.path = path
        self.map_info = map_info
        self.depart = depart
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
            drone_list.append(Drone(i, drone_path, self.depart[i]))
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
            turn = len(self.backup) + 1
            moves: list[str] = []
            links_used: list[frozenset[str]] = []
            drones_sorted = sorted(self.drone_list, key=Drone.key_tuple)

            for drone in drones_sorted:
                if drone.reach_the_end():
                    continue
                if drone.index == 0 and turn < drone.start_turn:
                    continue
                if drone.flyin:
                    next_zone = drone.drone_path[drone.index + 1].name
                    if not self.zone_state[next_zone].free_spot():
                        raise SimulationError(
                            f"turn {turn}: D{drone.drone_id} cannot land on "
                            f"'{next_zone}' (zone full)"
                        )
                    self.zone_state[next_zone].del_slot()
                    drone.switch_mode()
                    link_to_free = frozenset(
                        {
                            drone.return_position(),
                            next_zone,
                        }
                    )
                    self.links[link_to_free].add_slot()
                    drone.update_position()
                    moves.append(f"D{drone.drone_id}-{drone.return_position()}")
                else:
                    curr_zone = drone.return_position()
                    next_zone = drone.drone_path[drone.index + 1].name
                    link = self.links[frozenset({curr_zone, next_zone})]
                    if (
                        drone.drone_path[drone.index + 1].zone_status
                        == "restricted"
                    ):
                        if link.free_spot():
                            drone.switch_mode()
                            self.zone_state[curr_zone].add_slot()
                            link.del_slot()
                            moves.append(f"D{drone.drone_id}-{curr_zone}-{next_zone}")
                    elif link.free_spot() and self.zone_state[next_zone].free_spot():
                        self.zone_state[curr_zone].add_slot()
                        self.zone_state[next_zone].del_slot()
                        link.del_slot()
                        drone.update_position()
                        links_used.append(frozenset({curr_zone, next_zone}))
                        moves.append(f"D{drone.drone_id}-{drone.return_position()}")
            for el in links_used:
                self.links[el].add_slot()

            if not moves:
                raise SimulationError(f"turn {turn}: no drone can move")

            self.backup.append(moves)

    def print_backup(self) -> None:
        for el in self.backup:
            line = " ".join(el)
            print(line)
