from parser import Map
from zone import ZONE_INFO

# class Zone:
#     name: str
#     coordo: tuple[int, int]
#     zone_status: str = "normal"
#     color: str | None = None
#     max_drones: int | None = 1
#
# #class ZoneRestriction:
#     cost: int
#     access: bool
#     priority: bool
#
# ZONE_INFO: dict[str, ZoneRestriction] = {
#     "normal": ZoneRestriction(1, True, False),
#     "priority": ZoneRestriction(1, True, True),
#     "restricted": ZoneRestriction(2, True, False),
#     "blocked": ZoneRestriction(1, False, False),

# class Map:  # Regroupe les donnees pour dijka
#     nodes: dict[str, Zone]
#     connections: dict[str, dict[str, int]]
#     map_drone_lmt: int
#     start: Zone | None
#     end: Zone | None


class PathFinder:
    def __init__(self, data_parsed: Map):
        self.graph = data_parsed

    def dijkstra_not_djikarta(self) -> None:

        visited: set[str] = set()
        previous: dict[str, str] = {}
        start: str = self.graph.start.name
        end: str = self.graph.end.name

        dist = self.infinity(start)
        curr = start

        while True:
            for node in self.graph.connections[curr]:
 




    def infinity(self, start) -> dict[str, float]:

        dist: dict[str, float] = {}

        for k in self.graph.nodes:
            dist[k] = 0 if k == start else float("inf")
        return dist


""" 
    dijka, il faut un visited, et on marque le visited
    seulement une fois qu on a quitter le curr node et qu on a a safe les short path
    donc il faut garder track, de ou on est, ou on va et le cout pour les mouvements
    ensuite additioner ce coute pour chaque node, et une fois fait on bouge to
    the next node et on marque l ancien node comme visited. Ensuite, il suffira
    de backtrack la listes des nodes qu on a save, cette liste ne sera constituer 
    que des nodes aux coups les plus bas.

    Il faut aussi utiliser heapq (check si obligatoire ou si je peux contourner)

    
"""
