#!/usr/bin/python3
import sys

import pygame

from parser import PrinceOfParser
from algo import PathFinder
from engine import Engine
from booking import Clock
from timeline import Timeline
from render import Render
from errors import FlyInError


def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python3 fly_in.py <map_file>", file=sys.stderr)
        sys.exit(1)

    file: str = sys.argv[1]

    try:
        with open(file, "r", encoding="utf-8") as f:
            instruction = f.read()
    except OSError as e:  # introuvable, dossier, pas les droits...
        print(f"Error: cannot read '{file}': {e.strerror}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: '{file}' is not a text file", file=sys.stderr)
        sys.exit(1)

    try:
        p = PrinceOfParser(instruction)
        data_parsed = p.split_not_spit()  # return Map
        path = PathFinder(data_parsed)
        solution: list[str] = path.dijkstra_not_djikarta()  # return path
        clock = Clock(solution, data_parsed)
        clock.from_time_to_space()
        brain = Engine(solution, data_parsed, clock.start_turn)
        brain.engine_v12_biturbo()
        timeline = Timeline(
            brain.backup,
            data_parsed.start.name,
            data_parsed.end.name,
            data_parsed.map_drone_lmt,
        )
    except FlyInError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    brain.print_backup()  # la simulation est valide : on l affiche

    try:
        render = Render(data_parsed, timeline)
        render.run_run()
    except (pygame.error, OSError) as e:  # pas d ecran, asset manquant
        print(f"Warning: no graphical view ({e})", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # Ctrl+C : pas de traceback
        sys.exit(130)
