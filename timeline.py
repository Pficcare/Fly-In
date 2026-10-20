class Timeline:
    def __init__(self, backup, start, end, nb_drones) -> None:
        self.backup: list[list[str]] = backup  # result de la simulation final
        self.start: str = start
        self.end: str = end
        self.nb_d: int = nb_drones
        self.sequence: list = []

    def laps(self) -> int:
        return len(self.backup)

    def add_start_sequence(self) -> None:
        d_pos: dict[int, tuple[str, str]] = {}

        for d in range(1, self.nb_d + 1):
            d_pos[d] = (self.start, self.start)
        self.sequence.append(d_pos)

    def add_sequences(self) -> None:

        d_pos: dict[int, tuple[str, str]]

        for l in self.backup:
            d_pos = self.sequence[-1].copy()  # seq est une liste mais [-1] est un dic
            for el in l:
                tmp: list[str] = el.split("-")
                drone = tmp[0]
                d_id = int(drone[1::])
                if len(tmp) == 2:
                    zone = tmp[1]
                    d_pos[d_id] = (zone, zone)
                elif len(tmp) == 3:
                    src = tmp[1]
                    dest = tmp[2]
                    d_pos[d_id] = (src, dest)
                else:
                    raise ValueError
            self.sequence.append(d_pos)
