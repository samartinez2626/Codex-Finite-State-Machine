# BFS + DFS Pathfinding (Python Console)

## Run
```bash
python pathfinding.py
```

The script runs BFS and DFS on two built-in maps and prints:
- whether a path was found
- path length
- number of visited nodes
- rendered map overlays

## What to look for
- BFS should return a shortest path in these unweighted 4-direction grids.
- DFS can return a valid but longer path depending on stack exploration order.

## Reflection
On the included maps, BFS and DFS both find a path, but they usually explore differently.
BFS expands by layers (distance 0, then 1, then 2, ... from `S`), so the first time it reaches `G` the path is guaranteed shortest by edge count. That guarantee holds because each move has equal cost and the graph is unweighted.

DFS does not explore in concentric layers. It commits to one branch as far as possible, then backtracks when stuck. This behavior means DFS can reach `G` quickly on some layouts, but the returned path depends on neighbor order and is not guaranteed minimal. In practice, with the included neighbor order and stack push order, DFS often produces a longer path than BFS on maze-like maps because it follows a deep corridor before considering alternatives.

Visited counts can differ either way:
- DFS may visit fewer cells if it gets lucky and dives directly toward the goal.
- BFS may visit fewer cells when many deep dead ends exist, because BFS will still stop as soon as goal is dequeued at the shortest depth.

In short: use BFS when shortest path matters; use DFS for simple reachability checks or depth-oriented exploration.

## Monster Chase (Turn-Based)
A tiny console prototype is included in `pathfinding.py`:
- `P` = player, `M` = monster, `#` = wall, `.` = floor, `G` = optional exit
- Player moves with WASD
- Monster recomputes one-step chase path each turn using a mode flag (`BFS` or `DFS`)

Try it from a Python shell:
```python
from pathfinding import game_loop
game_loop("BFS")  # scarier, shortest-path chase
game_loop("DFS")  # goofier chase depending on branch order
```

## Extra credit ideas
- Add a seeded random map generator
- Animate exploration step-by-step with delays
- Track turn count and score in `game_loop()`
