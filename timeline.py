

class Timeline:
    def __init__(self, backup, start, end, nb_drones):
        self.backup: list[list[str]] = backup # result de la simulation final
        self.start: str = start
        self.end: str = end
        self.nb_d: int = nb_drones


    def laps(self):
        return len(self.backup)
    
    def drone_position(self):
        turn: int = 1
        drone_id: int = 1




