#!/usr/bin/python3
from parser import PrinceOfParser
from algo import PathFinder
from engine import Engine
from booking import Clock
from timeline import Timeline
from render import Render
import sys


def main() -> None:

    if len(sys.argv) != 2:
        print("Error input")
        sys.exit(1)

    file:str = sys.argv[1]

    try:
        with open(file, "r", encoding="utf-8") as f:
            instruction = f.read()
    except (Exception, OSError) as e:
        print(f"Error {e}")
        raise

    try:
        p = PrinceOfParser(instruction)
        data_parsed = p.split_not_spit() # return Map
        path = PathFinder(data_parsed)
        solution:list[str] = path.dijkstra_not_djikarta() # return path solved
        clock = Clock(solution, data_parsed)
        clock.from_time_to_space()
        brain = Engine(solution, data_parsed, clock.start_turn)
        brain.engine_v12_biturbo()
        brain.print_backup()
        timeline = Timeline(
            brain.backup,
            data_parsed.start.name,
            data_parsed.end.name,
            data_parsed.map_drone_lmt,
        )
        render = Render(data_parsed, timeline)
        render.run_run()

    except (Exception, ValueError) as e:
        print(f"Error {e}")


if __name__ == "__main__":
    main()

