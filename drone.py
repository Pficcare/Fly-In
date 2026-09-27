from parser import Map



# Creation de la class Drone et de sa logic

DIC_VOISIN = {}
PATH = []
DIC_ZONE = {}
ZONE: bool = True

class Drone:
    def __init__(self, drone_id:int, position:str):
        self._drone_id: int = drone_id
        self.position = position
        self.flyin:bool = False

       
    @property
    def drone_id(self) -> int:
        return self._drone_id

    def can_i_move(self):
        if ZONE is True:
            self.update_position()

    def update_position(self):
        self.position = DIC_VOISIN[self.position]

    def return_position(self) -> str:
        return self.position
    
    def switch_mode(self):
        if not self.flyin:
            self.flyin = True


class Engine:
    def __init__(self, path:list[str], map_info: Map):
        self.path = path
        self.start:set = set()
        self.end:set = set()
        self.map_info = map_info
        self.drone_list: list[Drone] = self.gen_drones()

    def gen_drones(self) -> list[Drone]:
        drone_list: list[Drone] = []
        position:str = self.path[0]

        for i in range(1, self.map_info.map_drone_lmt + 1):
            drone_list.append(Drone(i, position))
        return drone_list



    def engine(self):
       ... 

