import os

import pygame

from parser import Map
from timeline import Timeline

ASSETS: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assets"  # chemin absolu
)

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
        self.border: int = 60  # a check si ca reste 60, fix le bug afficage avec 30
        self.mid_x: int = self.width // 2  # A utiliser si scalex = 0
        self.mid_y: int = self.height // 2  # A utiliser si scaley = 0
        self.min_x: int
        self.max_x: int
        self.min_y: int
        self.max_y: int
        self.scale_x: int
        self.scale_y: int
        self.mesures()
        self.pixel_dic: dict[str, tuple[int, int]] = {}
        self.pixart()
        self.color_zone: dict[str, pygame.Color] = {}
        self.colors()
        self.zone_radius: int = 15
        self.drone_size: int = 24  
        self.drone_spacing: int = 20  
        self.frame_ms: int = 100  # duree d une image d animation
        self.drone_frames: list[pygame.Surface]
        self.death_frames: list[pygame.Surface]
        self.mothership_frames: list[pygame.Surface]
        self.background: pygame.Surface
        self.status_border: dict[str, tuple[str, int]] = {  # couleur, px
            "priority": ("green", 3),
            "restricted": ("orange", 3),
            "blocked": ("red", 5),  # pas de color pour normal
        }
        self.clock = pygame.time.Clock()
        self.window: pygame.Surface
        self.font: pygame.font.Font
        self.font_small: pygame.font.Font  # noms des zones
        self.last_turn: int = self.timeline.laps()
        self.turn: int = 0
        self.pause: bool = False
        self.turn_time: int = 0
        self.speeds: list[int] = [500, 250, 125, 2000, 1000]  # ms par tour
        self.speed_i: int = 0
        self.run: bool = True
        self.controls: str = (
            "SPACE pause · <-/-> tour · R reset · V vitesse · ESC quitter"
        )

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

    def colors(self) -> None:

        for zone in self.map.nodes.values():
            if zone.color in pygame.color.THECOLORS:
                self.color_zone[zone.name] = pygame.Color(zone.color)
            else:
                self.color_zone[zone.name] = pygame.Color("grey")  # defaut for now

    def load_strip(self, file: str, size: int) -> list[pygame.Surface]:

        
        sheet = pygame.image.load(os.path.join(ASSETS, file)).convert_alpha()
        side: int = sheet.get_height()
        frames: list[pygame.Surface] = []

        for i in range(sheet.get_width() // side):
            frame = sheet.subsurface((i * side, 0, side, side))
            frames.append(pygame.transform.scale(frame, (size, size)))
        return frames

    def load_background(self, file: str, veil: int) -> None:

        
        tile = pygame.image.load(os.path.join(ASSETS, file)).convert()
        self.background = pygame.Surface((self.width, self.height))
        for x in range(0, self.width, tile.get_width()):
            for y in range(0, self.height, tile.get_height()):
                self.background.blit(tile, (x, y))
        shade = pygame.Surface((self.width, self.height))
        shade.set_alpha(veil)  # voile noir : 0 = aucun, 255 = tout noir
        self.background.blit(shade, (0, 0))

    def run_run(self) -> None:

        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-In")
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)
        # convert/convert_alpha exigent une fenetre ouverte -> apres set_mode
        self.drone_frames = self.load_strip("drone_walk.png", self.drone_size)
        self.death_frames = self.load_strip("drone_death.png", self.drone_size)
        self.mothership_frames = self.load_strip("mothership_drop.png", 48)
        self.load_background("bg_purple_nebula.png", 120)

        while self.run:
            tick: int = self.clock.tick(60)  # ms depuis la frame precedente
            for el in pygame.event.get():
                if el.type == pygame.QUIT:
                    self.run = False
                elif el.type == pygame.KEYDOWN:
                    if el.key == pygame.K_ESCAPE:
                        self.run = False
                    elif el.key == pygame.K_SPACE:
                        self.pause = not self.pause
                    elif el.key == pygame.K_RIGHT:
                        self.turn = min(self.turn + 1, self.last_turn)
                        self.turn_time = 0
                    elif el.key == pygame.K_LEFT:
                        self.turn = max(self.turn - 1, 0)
                        self.turn_time = 0
                    elif el.key == pygame.K_r:
                        self.turn = 0
                        self.turn_time = 0
                        self.pause = False
                    elif el.key == pygame.K_v:
                        self.speed_i = (self.speed_i + 1) % len(self.speeds)

            if not self.pause and self.turn < self.last_turn:
                self.turn_time += tick
                if self.turn_time >= self.speeds[self.speed_i]:
                    self.turn += 1
                    self.turn_time = 0

            self.window.blit(self.background, (0, 0))
            self.draw_map()
            pygame.display.flip()

        pygame.quit()

    def draw_map(self) -> None:

        state_turn: dict[int, tuple[str, str]] = self.timeline.sequence[self.turn]

        for src, nbor in self.map.connections.items():
            for dest in nbor:
                if src < dest:
                    pygame.draw.line(
                        self.window,
                        "white",
                        self.pixel_dic[src],
                        self.pixel_dic[dest],
                        width=2,
                    )

        for zone in self.map.nodes.values():
            center: tuple[int, int] = self.pixel_dic[zone.name]
            pygame.draw.circle(
                self.window,
                self.color_zone[zone.name],
                center,
                self.zone_radius,
            )
            if zone.zone_status in self.status_border:
                color, width = self.status_border[zone.zone_status]
                pygame.draw.circle(self.window, color, center, self.zone_radius, width)
            name = self.font_small.render(zone.name, True, "white")
            rect = name.get_rect(
                midtop=(center[0], center[1] + self.zone_radius + 4)
            )
            self.window.blit(name, rect)

        drone_to_draw: dict[tuple[int, int], int] = {}  # pixel -> nb de drones
        for src, dest in state_turn.values():
            if src == dest:
                pos = self.pixel_dic[src]
            else:
                x = (self.pixel_dic[src][0] + self.pixel_dic[dest][0]) // 2
                y = (self.pixel_dic[src][1] + self.pixel_dic[dest][1]) // 2
                pos = (x, y)
            drone_to_draw[pos] = drone_to_draw.get(pos, 0) + 1

        start_end = (
            self.pixel_dic[self.map.start.name],
            self.pixel_dic[self.map.end.name],
        )
         ## avance avec le temps reel, pas avec les tours
        nb_frames: int = len(self.drone_frames)
        i_frame = pygame.time.get_ticks() // self.frame_ms % nb_frames
        sprite = self.drone_frames[i_frame]
        for pos, nb in drone_to_draw.items():
            if pos in start_end:
                self.window.blit(sprite, sprite.get_rect(center=pos))
                if nb > 1:
                    text = self.font.render(f"×{nb}", True, "white")
                    rect = text.get_rect(
                        midleft=(pos[0] + self.zone_radius + 4, pos[1])
                    )
                    self.window.blit(text, rect)
            else:
                for i in range(nb):
                    shift = (2 * i - (nb - 1)) * self.drone_spacing // 2
                    center = (pos[0] + shift, pos[1])
                    self.window.blit(sprite, sprite.get_rect(center=center))

        hud = f"Tour {self.turn}/{self.last_turn}"
        hud += f" · {self.speeds[self.speed_i]} ms/tour"
        if self.pause:
            hud += " · PAUSE"
        self.window.blit(self.font.render(hud, True, "white"), (8, 6))
        controls = self.font_small.render(self.controls, True, "white")
        rect = controls.get_rect(topright=(self.width - 8, 6))
        self.window.blit(controls, rect)



