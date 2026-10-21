from parser import Map
from timeline import Timeline
import pygame

# class Zone:
#     name: str
#     coordo: tuple[int, int]
#     zone_status: str = "normal"
#     color: str | None = None
#     max_drones: int | None = 1
#

# class Map:  # Regroupe les donnees pour dijka
#     nodes: dict[str, Zone]
#     connections: dict[str, dict[str, int]]
#     map_drone_lmt: int
#     start: Zone | None
#     end: Zone | None


class Render:
    def __init__(
        self, map_info: Map, timeline: Timeline, width: int = 1280, height: int = 720
    ) -> None:
        self.map = map_info
        self.timeline = timeline
        self.width: int = width
        self.height: int = height
        self.border: int = 30
        self.mid_x: int = self.width // 2  # A utiliser si scalex = 0
        self.mid_y: int = self.height // 2  # A utiliser si scaley = 0
        self.min_x: int
        self.max_x: int
        self.min_y: int
        self.max_y: int
        self.scale_x: int
        self.scale_y: int
        self.mesures()
        self.pixel_dic:dict[str, tuple[int, int]] = {}
        self.pixart()
        self.clock = pygame.time.Clock()
        self.window = None
        self.turn: int = 0
        self.pause: bool = False
        self.turn_time:int = 0
        self.run: bool = True


    def mesures(self) -> None:

        lx: list[int] = []
        ly: list[int] = []

        for el in self.map.nodes.values():
            x, y = el.coordo
            lx.append(x)
            ly.append(y)

        self.min_x, self.max_x = min(lx), max(lx)
        self.min_y, self.max_y = min(ly), max(ly)

        range_x: int = max(lx) - min(lx)
        range_y: int = max(ly) - min(ly)

        useable_scale_x = self.width - (2 * self.border)
        useable_scale_y = self.height - (2 * self.border)

        self.scale_x = useable_scale_x // range_x if range_x > 0 else 0
        self.scale_y = useable_scale_y // range_y if range_y > 0 else 0

    def pixart(self) -> None:

        for el in self.map.nodes.values():
            x, y = el.coordo
            px = (
                (x - self.min_x) * self.scale_x + self.border
                if self.scale_x > 0
                else self.mid_x
            )
            py = (
                self.height - self.border - ((y - self.min_y) * self.scale_y)
                if self.scale_y > 0
                else self.mid_y
            )

            self.pixel_dic[el.name] = (px, py)

    def run_run(self) -> None:
        
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-In")

        
        while self.run:

            self.clock.tick(60)
            for el in pygame.event.get():
                if el.type == pygame.QUIT:
                    self.run = False
            self.window.fill((40,40,40))
            pygame.display.flip()
        


        pygame.quit()










