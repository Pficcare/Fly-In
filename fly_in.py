#!/usr/bin/python3
from parser import PrinceOfParser



def main() -> None:

    try:
        with open("./maps/easy/02_simple_fork.txt", "r", encoding="utf-8") as file:
            instruction = file.read()

    # to add, sys management pour les maps au lieu d une en dure

    except (Exception, OSError) as e:
        print(f"Error {e}")
        raise e

    p = PrinceOfParser(instruction)
    data_parsed = p.split_not_spit()
    print (data_parsed)
    # dijkarta_not_djakarta(data_parsed)


if __name__ == "__main__":
    main()

