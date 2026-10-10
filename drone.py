from zone import ZONE_INFO, Zone


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
