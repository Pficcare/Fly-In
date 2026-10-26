#!/usr/bin/python3
from dataclasses import dataclass

from errors import ParseError
from zone import ZONE_INFO, Zone

HUB_KEYS = frozenset(["nb_drones", "start_hub", "end_hub", "hub", "connection"])
ZONE_KEYS = frozenset(["zone", "color", "max_drones"])
LINK_KEYS = frozenset(["max_link_capacity"])


# @dataclass(frozen=True)
# class Zone:
#     name: str
#     coordo: tuple[int, int]
#     zone_status: str = "normal"
#     color: str | None = None
#     max_drones: int | None = 1


@dataclass
class Map:  # Regroupe les donnees pour dijka
    nodes: dict[str, Zone]
    connections: dict[str, dict[str, int]]
    map_drone_lmt: int
    start: Zone
    end: Zone


class PrinceOfParser:
    def __init__(self, instruction: str) -> None:
        self.nodes: dict[str, Zone] = {}
        self.connections: dict[str, dict[str, int]] = {}
        self.instruction = instruction
        self.map_drone_lmt = 0  # 0 = nb_drones pas encore lu
        self.start: Zone | None = None
        self.end: Zone | None = None

    def split_not_spit(self) -> Map:
        for num, line in enumerate(self.instruction.splitlines(), start=1):
            line, _, _ = line.partition("#")

            if not line.strip():  # si que " "
                continue
            hub, sep, datas = line.partition(":")
            hub = hub.strip()

            if not sep or hub not in HUB_KEYS:
                raise ParseError(num, f"unknown line type '{line.strip()}'")
            if hub != "nb_drones" and self.map_drone_lmt == 0:
                raise ParseError(num, "first line must be 'nb_drones: <nb>'")
            if line.count("[") > 1 or line.count("[") != line.count("]"):
                raise ParseError(num, "invalid brackets")
            if "]" in line and not line.rstrip().endswith("]"):
                raise ParseError(num, "text after ']'")

            if hub == "nb_drones":
                if self.map_drone_lmt != 0:
                    raise ParseError(num, "nb_drones defined twice")
                nb = self.to_int(datas, num, "nb_drones")
                self.map_drone_lmt = nb

            elif hub == "start_hub" or hub == "end_hub":
                datas, _, params = datas.partition("[")
                if len(datas.split()) != 3:
                    raise ParseError(num, f"expected '{hub}: <name> <x> <y>'")
                node, sx, sy = datas.split()
                if "-" in node:
                    raise ParseError(num, f"zone name '{node}' has a dash")
                if node in self.nodes:
                    raise ParseError(num, f"zone '{node}' already defined")
                (x, y) = self.convertion(sx, sy, num)
                meta = self.param_or_not_param(params, num, ZONE_KEYS)
                color1: str | None = meta.get("color")
                zone1: str = meta.get("zone", "normal")
                z = Zone(node, (x, y), zone1, color1, max_drones=None)
                if hub == "start_hub":
                    if self.start is not None:
                        raise ParseError(num, "start_hub defined twice")
                    self.start = z
                else:
                    if self.end is not None:
                        raise ParseError(num, "end_hub defined twice")
                    self.end = z
                self.nodes[node] = z
                self.connections[node] = {}

            elif hub == "hub":
                datas, _, params = datas.partition("[")
                if len(datas.split()) != 3:
                    raise ParseError(num, "expected 'hub: <name> <x> <y>'")
                node, sx, sy = datas.split()
                if "-" in node:
                    raise ParseError(num, f"zone name '{node}' has a dash")
                if node in self.nodes:
                    raise ParseError(num, f"zone '{node}' already defined")
                (x, y) = self.convertion(sx, sy, num)
                meta = self.param_or_not_param(params, num, ZONE_KEYS)
                color2: str | None = meta.get("color")
                max_d = self.to_int(
                    meta.get("max_drones", "1"), num, "max_drones"
                )
                zone: str = meta.get("zone", "normal")
                z = Zone(node, (x, y), zone, color2, max_d)
                self.nodes[node] = z
                self.connections[node] = {}

            elif hub == "connection":
                datas, _, params = datas.partition("[")
                datas = datas.strip()
                if len(datas.split()) != 1 or datas.count("-") != 1:
                    raise ParseError(num, "expected 'connection: <a>-<b>'")
                node, nbor = datas.split("-")
                if node not in self.nodes:
                    raise ParseError(num, f"unknown zone '{node}'")
                if nbor not in self.nodes:
                    raise ParseError(num, f"unknown zone '{nbor}'")
                if node == nbor:
                    raise ParseError(num, f"zone '{node}' linked to itself")
                if nbor in self.connections[node]:
                    raise ParseError(num, f"duplicate connection '{datas}'")
                if not params:
                    nb = 1
                else:
                    meta = self.param_or_not_param(params, num, LINK_KEYS)
                    snb = meta.get("max_link_capacity", "1")
                    nb = self.to_int(snb, num, "max_link_capacity")
                self.connections[node][nbor] = nb
                self.connections[nbor][node] = nb

        if self.map_drone_lmt == 0:
            raise ParseError(None, "empty map: missing 'nb_drones'")
        if self.start is None:
            raise ParseError(None, "missing 'start_hub'")
        if self.end is None:
            raise ParseError(None, "missing 'end_hub'")

        return Map(self.nodes, self.connections, self.map_drone_lmt, self.start, self.end)

    @staticmethod
    def convertion(x: str, y: str, num: int) -> tuple[int, int]:
        try:
            a = int(x)
            b = int(y)
        except ValueError:
            raise ParseError(
                num, f"coordinates must be integers, got '{x} {y}'"
            ) from None
        return (a, b)

    @staticmethod
    def to_int(value: str, num: int, what: str) -> int:
        value = value.strip()
        try:
            nb = int(value)
        except ValueError:
            raise ParseError(
                num, f"{what} must be a positive integer, got '{value}'"
            ) from None
        if nb < 1:
            raise ParseError(num, f"{what} must be positive, got {nb}")
        else:
            return nb

    @staticmethod
    def param_or_not_param(
        datas: str, num: int, allowed: frozenset[str]
    ) -> dict[str, str]:

        param_values: dict[str, str] = {}

        # "zone=restricted color=red]" -> {"zone": "restricted", ...}
        for el in datas.strip().strip("]").split():
            p1, equal, p2 = el.partition("=")
            if not equal or not p1 or not p2 or "=" in p2:
                raise ParseError(num, f"invalid metadata '{el}' (key=value)")
            if p1 not in allowed:
                raise ParseError(num, f"unknown metadata '{p1}'")
            if p1 in param_values:
                raise ParseError(num, f"metadata '{p1}' given twice")
            if p1 == "zone" and p2 not in ZONE_INFO:
                raise ParseError(num, f"invalid zone type '{p2}'")
            param_values[p1] = p2

        return param_values


# class PrinceOfParser:
#     def __init__(self, instruction: str):
#         self.vertex: dict = {}
#         self.instruction = instruction
#         self.map_drone_lmt = 0
#
#     def split_not_spit(self):
#         # definir dees gabarits pour stocker les valeurs:
#         self.start_hub: dict = {"coordo": (0, 0), "color": None}
#         self.hub: dict = {
#             "coordo": (0, 0),
#             "zone": "normal",
#             "color": None,
#             "max_drones": 1,
#         }
#         self.end_hub: dict = {"coordo": (0, 0), "color": None}
#         self.list_param: list = []
#
#         for line in self.instruction.strip().splitlines():
#             line, _, _ = line.partition("#")
#             if not line.strip():  # si que " " return false
#                 continue
#             hub, _, datas = line.partition(":")
#             hub = hub.strip()
#             if hub not in HUB_KEYS:
#                 raise KeyError
#             if hub == "nb_drones":
#                 nb = int(datas)
#                 self.map_drone_lmt = nb
#
#             elif hub == "start_hub" or hub == "end_hub":
#                 id_node = (
#                     self.start_hub.copy()
#                 )  # sans cpy,on passe l adresse a id donc le meme dict
#                 id_node["voisin"] = {}
#                 if hub == "end_hub":
#                     id_node = self.end_hub.copy()
#                     id_node["voisin"] = {}
#                 datas, _, params = datas.partition("[")
#                 node, x, y = datas.split()
#                 (x, y) = self.convertion(x, y)
#                 id_node["coordo"] = (x, y)
#                 p1, p2 = params.split("=")
#                 p2 = p2.strip("]")
#                 if p1 in id_node:
#                     id_node[p1] = p2
#                 else:
#                     print(f"Error {p1} is not a valid data")
#                 self.vertex[node] = id_node
#
#             elif hub == "hub":
#                 datas, _, params = datas.partition("[")
#                 node, x, y = datas.split()
#                 (x, y) = self.convertion(x, y)
#                 id_node = self.hub.copy()
#                 id_node["voisin"] = {}
#                 id_node["coordo"] = (x, y)
#                 self.list_param = params.split()
#                 for i in range(len(self.list_param)):
#                     data = self.list_param[i]
#                     p1, p2 = data.split("=")
#                     p2 = p2.strip("]")
#                     if p1 in id_node and p1 == "max_drones":
#                         id_node[p1] = int(p2)
#                     elif p1 in id_node:
#                         id_node[p1] = p2
#                     else:
#                         raise ValueError
#                         print(f"{p1} is not valid")
#                 self.vertex[node] = id_node
#
#             elif hub == "connection":
#                 datas, _, params = datas.partition("[")
#                 datas = datas.strip()
#                 if not params:
#                     node, nbor = datas.split("-")
#                     node = node.strip()
#                     nbor = nbor.strip()
#                     nb = 1
#                 else:
#                     node, nbor = datas.split("-")
#                     node = node.strip()
#                     nbor = nbor.strip()
#                     link, nb = params.split("=")
#                     link = link.strip()
#                     nb = nb.strip("]")
#                     nb = int(nb)
#                 if node not in self.vertex or nbor not in self.vertex:
#                     raise KeyError
#                 self.vertex[node]["voisin"][nbor] = nb
#                 self.vertex[nbor]["voisin"][node] = nb
#
#         print(self.vertex.items())


# def split_not_spit(self)-> dict | None:
#     for line in self.instruction.strip().splitlines():
#         if not line.strip():
#             continue
#         first, _, end = line.partition(":")
#         first, end = first.strip(), end.strip()
#         if first == "nb_drones":
#             try:
#                 self.drone_lmt = int(end)
#             except ValueError as e:
#                 raise
#         elif first == "start_hub":
#             node_id, _, param = end.partition("[")
#             node, x, y = node_id.split()
#             color, value = param.split("=")
#             value = value.strip("]")
#             try:
#                 x = int(x)
#                 y = int(y)
#             except ValueError as e:
#                 raise
#             self.vertex[node] = {"coord":(x,y), color: value}
#         elif first == "hub":
#             node_id, _, param = end.partition("[")
#             node, x, y = node_id.split()
#             color_info,_, max_drones= param.partition(" ")
#             color, value = color_info.split("=")
#             if "max_drone" in end:
#                 max_drone, nb = max_drones.split("=")
#                 nb = nb.strip("]")
#             else:
#                 nb = -1
#                 max_drone = "max_drone"
#             try:
#                 x = int(x)
#                 y = int(y)
#             except ValueError as e:
#                 raise
#             self.vertex[node] = {"coord":(x,y), color: value, max_drone:nb}
#         elif first == "end_hub":
#             node_id, _, param = end.partition("[")
#             node, x, y = node_id.split()
#             if not param.split("="):
#                 return None
#             color, value = param.split("=")
#             value = value.strip("]")
#             try:
#                 x = int(x)
#                 y = int(y)
#             except ValueError as e:
#                 raise
#             self.vertex[node] = {"coord":(x,y), color: value}
#         elif first == "connection":
#             node_nbor, _, param = end.partition(" ")
#             node, nbor = node_nbor.split("-")
#             max_link, _, nb = param.partition("=")
#             max_link = max_link.strip("[")
#             nb = nb.strip("]")
#             try:
#                 nb = int(nb)
#             except ValueError as e:
#                 raise
#             self.vertex[node][max_link] = nb
#             self.vertex[node]["neihgbor"] = self.neibor.append(nbor)
#             self.vertex[nbor]["neihgbor"] = self.neibor.append(node)
#     return self.vertex


# def split_my_ass(text:str):
#
#     vertex:dict = {}
#     neibor:list = []
#
#     # Split le text en ligne:
#     for line in text.strip().splitlines(): # strip nettoie les blank en trop
#         if not line.strip():
#             continue
#         start, _, txt = line.partition(":") # split in 3, what is before: the sep(:)and after:
#         start, txt = start.strip(), txt.strip()
#         if start == "nb_drones":
#             drones_data = int(txt)
#         elif "hub" in start:
#             node_info, _, param = txt.partition("[")
#             node,x,y = node_info.split()
#             param.rsplit("]")
#             colorinfo, max_drones = param.split()
#             color,b = colorinfo.split("=")
#             maxd, nb = max_drones.split("=")
#             vertex[node] = {'pos': (x,y), 'color':'b', 'max_d':nb, 'neibor': []}
#         elif "connection" in start:
#             _,nbor = txt.split("-")
#             if _ == "start":
#                 nbor,_,maxlink = nbor.partition('[')
#                 maxlink.rsplit(']')
#                 maxlink, nb = maxlink.split('=')
#                 vertex[node]['maxlink'] = nb
#                 vertex[node]['neibor'].append(nbor)
#             else:
#                 vertex[node]['neibor'].append(nbor)
#
#     print(vertex)


# Exemple:gate1 1 0[color=orange max_drones=1]
