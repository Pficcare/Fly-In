*This project has been created as part of the 42 curriculum by pficcare.*

# Fly-in

## Description

Fly-in routes a fleet of drones from a unique `start` zone to a unique `end` zone
through a graph of connected zones, in the **fewest possible simulation turns**.
Zones have a movement cost (`normal`/`priority` = 1 turn, `restricted` = 2 turns,
`blocked` = impassable) and a capacity (`max_drones`); connections have a capacity
too (`max_link_capacity`). The program parses a map file, computes a route,
simulates the drones turn by turn while respecting every constraint, and prints
one line per turn.

## Instructions

```
make install                     # create venv/ and install the dependencies
python3 fly_in.py <map_file>     # run the simulation on a map
make lint                        # flake8 + mypy with the required flags
make clean                       # remove caches
```

A graphical view is planned behind an option (see *Visual representation*):

```
python3 fly_in.py <map_file> --visual
```

## Algorithm choices and implementation

### Project structure

Each step takes a clear input and returns a clear output, so it can be tested on
its own:

| File | Role |
|---|---|
| `parser.py` | map file → `Map` (zones, connections, number of drones) |
| `zone.py` | `Zone` (frozen dataclass) and `ZONE_INFO` (rules of each zone type) |
| `algo.py` | `PathFinder`: path search |
| `drone.py` | `Drone`: carries its own data (id, path, position, in-flight state) |
| `engine.py` | `Engine`: runs the turns; `ZoneState` / `LinkZone`: capacity counters |
| `fly_in.py` | entry point: reads the argument, chains the steps, prints the result |

### Zone model

A `Zone` is a **frozen** dataclass: the parsed graph is never modified, so the
path search can reuse it safely. The rules of each zone type (cost, access,
priority) live in a dictionary `ZONE_INFO` of frozen `ZoneRestriction` objects,
which keeps the rules in one place and readable.

### Path search

`PathFinder` runs a hand-written **Dijkstra** (no graph library) weighted by the
cost of the destination zone (`restricted` = 2), skipping `blocked` zones. All
drones currently follow this single shortest path.

On the provided maps, this already meets every reference target of the subject
(e.g. simple fork: 6 turns for a target of 8, circular loop: 15 for 15).
Planned improvements: preferring `priority` zones on equal cost, then a
**min-cost max-flow** (successive shortest paths, with Dijkstra as the inner
search) to spread drones over several paths on maps with parallel corridors.

### Simulation engine

- **The Engine is the only decision-maker.** Drones and counters only hold
  information; the Engine reads them, decides, then updates them.
- **One path per drone**, stored in the drone itself, so a multi-path router can
  be plugged in later without changing the Engine.
- **Capacity counters:** `ZoneState` and `LinkZone` count the *remaining* places.
  Each connection has **one** counter whatever the direction (dictionary keyed by
  a `frozenset` of the two zone names), otherwise its capacity would be doubled.
- **Turn order replaces a two-phase evaluation:** each turn, drones are sorted
  (in flight first, then closest to the end, then by id). Drones in front move
  first, so a place they free is usable by the drones behind them **in the same
  turn**, as the subject requires.
- **Connections are freed at the end of the turn**; zones are freed immediately.
- **Restricted zones:** at take-off the drone frees its zone and reserves both the
  connection and the destination zone; it must land on the next turn, which frees
  the connection. While in flight it is printed as `D<id>-<zone1>-<zone2>`.
- **Deadlock guard:** every state change writes a move, so a turn with no move
  while drones remain means the simulation is stuck; the Engine stops instead of
  looping forever.
- **History:** each turn is stored as a list of moves; the score is the number of
  turns.

## Visual representation

*In progress.* The plan:

- **pygame** window, opened only with `--visual`, so the text output stays clean
  and the program still works on a machine without a display.
- The renderer only reads the `Map` and the **printed output**, not the Engine
  internals: it shows exactly what the program outputs, and does not depend on
  the routing algorithm. Zone names contain no dash, so each move can be split
  without ambiguity.
- Zones are drawn with their map `color`, connections with a thickness based on
  their capacity, and drones move smoothly between turns (interpolation with
  easing). A drone in flight to a `restricted` zone is shown in the middle of the
  connection, which makes the 2-turn cost visible.
- Controls: pause, step forward/back, speed, restart.

## Example

Input (`maps/easy/02_simple_fork.txt`):

```
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

Output (6 turns):

```
D1-junction D2-junction
D1-path_a D3-junction
D1-goal D2-path_a D4-junction
D2-goal D3-path_a
D3-goal D4-path_a
D4-goal
```

## Resources

- Dijkstra's algorithm — https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Minimum-cost flow — https://en.wikipedia.org/wiki/Minimum-cost_flow_problem
- Python documentation — https://docs.python.org/3/
- pygame documentation — https://www.pygame.org/docs/

### AI usage

Claude (Anthropic) was used as a tutor: explaining concepts (Dijkstra, flows,
simulation order, Python syntax), reviewing code and running test traces on the
maps to find bugs. 
The design decisions and the code were written by Pficcre.
