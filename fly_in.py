#!/usr/bin/python3
from parser import PrinceOfParser
from algo import PathFinder
from drone import Engine


def main() -> None:

    try:
        with open("./maps/easy/02_simple_fork.txt", "r", encoding="utf-8") as file:
            instruction = file.read()

    # to add, sys management pour les maps au lieu d une en dure

    except (Exception, OSError) as e:
        print(f"Error {e}")
        raise

    p = PrinceOfParser(instruction)
    data_parsed = p.split_not_spit() # return Map
    print (data_parsed)
    path = PathFinder(data_parsed)
    solution:list[str] = path.dijkstra_not_djikarta() # return path solved
    print (solution)
    brain = Engine(solution, data_parsed)


if __name__ == "__main__":
    main()

