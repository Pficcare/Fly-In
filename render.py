from parser import Map
from timeline import Timeline

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
        self.mid_x: int = self.width // 2  # A utiliser si x = 0
        self.mid_y: int = self.height // 2  # A utiliser si y = 0
        self.min_x: int
        self.max_x: int
        self.min_y: int
        self.max_y: int
        self.scale_x: int
        self.scale_y: int
        self.mesures()
        self.pixel_dic:dict[str, tuple[int, int]] = {}
        self.pixart()


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

        pos: int = 0

        lx: list[int] = []
        ly: list[int] = []

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
