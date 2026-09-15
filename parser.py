#!/usr/bin/python3
# import sys
from dataclasses import dataclass

HUB_KEYS = frozenset(["nb_drones", "start_hub", "end_hub", "hub", "connection"])

@dataclass(frozen=True)
class Zone:
    name: str
    coordo: tuple[int,int]
    zone_status: str = "normal"
    color:str | None = None
    max_drones:int = 1

class PrinceOfParser:
    def __init__(self, instruction: str):
        self.vertex: dict = {}
        self.instruction = instruction
        self.map_drone_lmt = 0
        self.start: Zone| None
        self.end: Zone | None

    def split_not_spit(self):
        for line in self.instruction.strip().splitlines():
            line, _, _ = line.partition("#")

            if not line.strip():  # si que " " 
                continue
            hub, _, datas = line.partition(":")
            hub = hub.strip()

            if hub not in HUB_KEYS:
                raise KeyError

            if hub == "nb_drones":
                nb = self.to_int(datas)
                self.map_drone_lmt = nb
                
            elif hub == "start_hub" or hub == "end_hub":
                datas, _, params = datas.partition("[")
                node, x, y = datas.split()
                (x, y) = self.convertion(x, y)
                if len(params) != 2:
                    raise ValueError
                p1, p2 = params.split("=") #color=green
                color: str | None = None
                p2 = p2.strip("]")
                if p1 == "color":
                    color = p2
                elif p1 != "max_drones":
                    raise ValueError
                z = Zone(node,(x,y),"normal", color)
                if hub == "start_hub":
                    self.start = z
                else:
                    self.end = z
                self.vertex[node] = z

            elif hub == "hub":
                datas, _, params = datas.partition("[")
                node, x, y = datas.split()
                (x, y) = self.convertion(x, y)
                id_node = self.hub.copy()
                id_node["voisin"] = {}
                id_node["coordo"] = (x, y)
                self.list_param = params.split()
                for i in range(len(self.list_param)):
                    data = self.list_param[i]
                    p1, p2 = data.split("=")
                    p2 = p2.strip("]")
                    if p1 in id_node and p1 == "max_drones":
                        id_node[p1] = int(p2)
                    elif p1 in id_node:
                        id_node[p1] = p2
                    else:
                        raise ValueError
                        print(f"{p1} is not valid")
                self.vertex[node] = id_node

            elif hub == "connection":
                datas, _, params = datas.partition("[")
                datas = datas.strip()
                if not params:
                    node, nbor = datas.split("-")
                    node = node.strip()
                    nbor = nbor.strip()
                    nb = 1
                else:
                    node, nbor = datas.split("-")
                    node = node.strip()
                    nbor = nbor.strip()
                    link, nb = params.split("=")
                    link = link.strip()
                    nb = nb.strip("]")
                    nb = int(nb)
                if node not in self.vertex or nbor not in self.vertex:
                    raise KeyError
                self.vertex[node]["voisin"][nbor] = nb
                self.vertex[nbor]["voisin"][node] = nb

        print(self.vertex.items())

         

    @staticmethod
    def convertion(x: str, y: str) -> tuple[int, int]:
        try:
            a = int(x)
            b = int(y)
        except ValueError:
            raise ValueError
        return (a, b)

    @staticmethod
    def to_int(value: str) -> int:
        try:
            nb = int(value)
        except ValueError:
            raise ValueError
        if nb < 1:
            raise ValueError
        else:
            return nb



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


def main() -> None:

    try:
        with open("./maps/easy/02_simple_fork.txt", "r", encoding="utf-8") as file:
            instruction = file.read()

    except (Exception, OSError) as e:
        print(f"Error {e}")
        raise e

    p = PrinceOfParser(instruction)
    parsed = p.split_not_spit()


if __name__ == "__main__":
    main()
