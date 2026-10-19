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
| `booking.py` | `Clock`: reservation table, plans the timed itinerary of every drone |
| `fly_in.py` | entry point: reads the argument, chains the steps, prints the result |

### Zone model

A `Zone` is a **frozen** dataclass: the parsed graph is never modified, so the
path search can reuse it safely. The rules of each zone type (cost, access,
priority) live in a dictionary `ZONE_INFO` of frozen `ZoneRestriction` objects,
which keeps the rules in one place and readable.

### Path search

`PathFinder` runs a hand-written **Dijkstra** (no graph library) weighted by the
cost of the destination zone (`restricted` = 2), skipping `blocked` zones. All
drones follow this single shortest path. On equal number of turns, it prefers
the path with the most `priority` zones (see below).

### Why Dijkstra was not replaced by a multi-path router

The first plan was a **min-cost max-flow** (successive shortest paths, with
Dijkstra as the inner search) to spread drones over several paths. Before
writing it, the possible gain was measured on the 10 provided maps:

- **7 maps out of 10 have a max flow of 1**: every drone must cross the same
  connection or zone of capacity 1 (e.g. `maze_c2-bottleneck`, `start-gate_hell1`).
  There, no router can do better than a single path.
- On those maps the score is bounded below by `L + n - 1` (`L` = turns of the
  shortest path, `n` = number of drones). On the challenger map:
  `19 + 25 - 1 = 43`, whatever the routing.
- **Reverse arcs** (the part of the flow that can undo a previous choice) gain
  **0 turns** on all 10 maps.
- Several paths only help **2 maps**: simple fork (6 → 4) and priority puzzle
  (8 → 6), which already meet the subject's targets with one path.
- A simpler variant (rerun Dijkstra after removing the used capacity) gave the
  same results, but needed a copy of every capacity: too much complexity for
  these 2 maps.

The measures showed that the turns were lost **in the simulation, not in the
routing**: on `restricted` zones, the first engine only let one drone through
every 2 turns (challenger: 67 turns instead of 43). So Dijkstra stays as it is,
and the effort went into the scheduling (see *Scheduling: reservation table*).

### Priority zones (ambiguity in the subject)

The subject only says that a `priority` zone *"costs 1 turn but should be
prioritized in pathfinding"*. It does not say how strong that preference is.
Interpretation chosen here:

- `priority` is a **tie-break only**: between paths with the same number of
  turns, the one with the most `priority` zones wins.
- A longer path is **never** chosen just to cross `priority` zones: the score is
  the number of turns, so that would only lose turns.

Implementation: the preference is put into the costs instead of adding a
special rule to Dijkstra. With `K` = number of zones of the map:

| Zone type | Turns | Cost in Dijkstra |
|---|---|---|
| `normal` | 1 | `K` |
| `priority` | 1 | `K - 1` |
| `restricted` | 2 | `2K` |

A path enters at most `K - 1` zones, so all the `- 1` bonuses together are
always worth less than one turn (`K`): a longer path can never win. The search
stays generic, and the same costs will feed the min-cost max-flow.

Check: on a variant of `priority_puzzle` where both paths take 4 turns, the
path through the two `priority` zones is chosen; on the 10 provided maps, scores
and paths are unchanged.

### Simulation engine

- **`Clock` decides when, the Engine simulates.** `Clock` (see *Scheduling:
  reservation table*) gives each drone its departure turn, stored in the drone
  (`start_turn`); a drone stays in `start` until that turn. After that, the
  Engine runs every turn: drones and counters only hold information, the Engine
  reads them, checks the capacities, then updates them.
- **One path per drone**, stored in the drone itself, so a multi-path router can
  be plugged in later without changing the Engine.
- **Capacity counters:** `ZoneState` and `LinkZone` count the *remaining* places.
  Each connection has **one** counter whatever the direction (dictionary keyed by
  a `frozenset` of the two zone names), otherwise its capacity would be doubled.
- **Turn order replaces a two-phase evaluation:** each turn, drones are sorted
  (closest to the end first, then in flight, then by id). Drones in front move
  first, so a place they free is usable by the drones behind them **in the same
  turn**, as the subject requires. On a tie, the drone in flight goes first: it
  lands and frees the connection, so a drone waiting in its starting zone can
  take that connection in the same turn. The first engine sorted drones in
  flight first; with landing on a `restricted` zone (see below), a drone in
  flight was then checked before the drone in front had left the zone, and the
  landing failed (challenger, turn 9).
- **Connections are freed at the end of the turn**; zones are freed immediately.
- **Restricted zones:** at take-off the drone frees its zone and takes **only the
  connection**. It must land on the next turn: landing takes the destination
  zone and frees the connection. The zone is taken at landing, not at take-off,
  because the departure turns from `Clock` guarantee it will be free then; this
  is what lets one drone through every turn instead of every 2 turns. If the zone
  is still full at landing, the Engine raises an error, since a drone cannot wait
  on a connection: it is a guard in case `Clock` and the Engine ever disagree.
  While in flight the drone is printed as `D<id>-<zone1>-<zone2>`.
- **Deadlock guard:** every state change writes a move, so a turn with no move
  while drones remain means the simulation is stuck; the Engine stops instead of
  looping forever.
- **History:** each turn is stored as a list of moves; the score is the number of
  turns.

### Scheduling: reservation table

**The problem with the first engine.** A drone flying to a `restricted` zone
spends one turn on the connection and **cannot wait there**: it must land on the
next turn. When it takes off, the Engine does not know if the zone will be free
on the next turn, so it reserves the zone at take-off to be safe. The result is
one drone every 2 turns on a `restricted` zone: `L + 2(n - 1)` turns instead of
`L + n - 1` (challenger: 67 instead of 43).

**The idea:** instead of deciding turn by turn, compute the **full timed
itinerary of every drone before the simulation**. A take-off toward a
`restricted` zone is then only planned if the landing turn is known to be free.

How it works (`booking.py`, class `Clock`):

1. `itinerary(start_turn)` builds the list of steps of a drone leaving `start`
   at a given turn: each step says on which turn it uses which zone and which
   connection. A `restricted` zone gives two steps (the turn on the connection,
   then the landing).
2. Two tables count the reservations: **zone × turn** and **connection × turn**.
3. `valid_step` checks that no step of the itinerary exceeds a capacity.
4. Drones are planned one after the other. For each drone, the start turn is
   increased until the itinerary is valid, then `book` stores it.

Rules used in the tables:

- A zone is counted **at the end of the turn** where a drone arrives.
- A `restricted` zone is only needed **at landing**, not at take-off.
- A connection is counted on the turn the drone takes it.

Why this choice:

- **No deadlock possible.** A drone only waits in `start`, which has unlimited
  capacity; once in the air, its plan never changes. A drone can never be
  stuck behind another one.
- **A plan is never questioned.** A reservation is only made when the whole
  itinerary is valid, so later drones adapt to earlier ones, never the reverse.
- **The search is short.** All drones share the same path, so the only free
  parameter is the start turn. It does not need to restart from 0 for the next
  drone: every earlier start turn already failed because of reservations that
  are still there.
- **It reaches the lower bound.** `Clock` reaches `L + n - 1` on the provided
  maps where one path is optimal, e.g. challenger 43 turns (67 with the first
  engine) and circular loop 10 (15 before). See *Results*.

### Results

Measured with `python3 fly_in.py <map>` on the 10 provided maps. Every output
was also replayed by an independent checker (zone and connection capacities,
moves along the path, landing on the turn after a take-off, all drones
delivered): all 10 are valid.

| Map | Drones | First engine | Reservation table | Subject target |
|---|---|---|---|---|
| easy/01_linear_path | 2 | 4 | 4 | < 10 |
| easy/02_simple_fork | 4 | 6 | 6 | < 10 |
| easy/03_basic_capacity | 4 | 4 | 4 | < 10 |
| medium/01_dead_end_trap | 5 | 8 | 8 | 10–30 |
| medium/02_circular_loop | 6 | 15 | **10** | 10–30 |
| medium/03_priority_puzzle | 5 | 8 | 8 | 10–30 |
| hard/01_maze_nightmare | 8 | 13 | 13 | < 60 |
| hard/02_capacity_hell | 12 | 16 | 16 | < 60 |
| hard/03_ultimate_challenge | 15 | 26 | 26 | < 60 |
| challenger/01_the_impossible_dream | 25 | 67 | **43** | 45 (record) |

Only 2 maps change: circular loop and challenger are the only ones where the
chosen path crosses a `restricted` zone, which the first engine let through one
drone every 2 turns. Four other maps contain `restricted` zones, but Dijkstra's
path avoids them, so nothing changes there. On the challenger map, 43 is
also the lower bound `19 + 25 - 1`: no routing can do better.

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
D1-junction
D1-path_a D2-junction
D1-goal D2-path_a D3-junction
D2-goal D3-path_a D4-junction
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
