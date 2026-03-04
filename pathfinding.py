from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

Pos = Tuple[int, int]  # (row, col)
Grid = List[List[str]]


EXAMPLE_MAP_1 = """
##########
#S.......#
#.######.#
#......#G#
##########
""".strip("\n")

EXAMPLE_MAP_2 = """
############
#S.....#...#
###.##.#.#.#
#...#..#.#G#
#.###..#...#
#..........#
############
""".strip("\n")

CHASE_MAP = """
############
#P....#....#
#.#.#.#.##.#
#.#...#....#
#.###.####.#
#...#....M.#
#.##.##.#..#
#....#...G.#
############
""".strip("\n")


def parse_grid(text: str) -> Tuple[Grid, Pos, Pos]:
    """
    Convert a multiline string map into a grid plus start and goal positions.

    Map legend:
    '#' wall
    '.' floor
    'S' start (exactly one)
    'G' goal (exactly one)
    """
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Grid text is empty")

    width = len(lines[0])
    if any(len(line) != width for line in lines):
        raise ValueError("Grid rows must all have the same width")

    grid: Grid = [list(line) for line in lines]
    start: Optional[Pos] = None
    goal: Optional[Pos] = None

    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == "S":
                if start is not None:
                    raise ValueError("Grid must contain exactly one S")
                start = (r, c)
            elif ch == "G":
                if goal is not None:
                    raise ValueError("Grid must contain exactly one G")
                goal = (r, c)
            elif ch not in {"#", "."}:
                raise ValueError(f"Unsupported cell '{ch}' at {(r, c)}")

    if start is None or goal is None:
        raise ValueError("Grid must contain one S and one G")

    return grid, start, goal


def neighbors(grid: Grid, node: Pos) -> List[Pos]:
    """Return valid 4-direction neighbors that are not walls."""
    r, c = node
    h, w = len(grid), len(grid[0])
    out: List[Pos] = []

    for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] != "#":
            out.append((nr, nc))

    return out


def reconstruct_path(parent: Dict[Pos, Pos], start: Pos, goal: Pos) -> Optional[List[Pos]]:
    """Reconstruct path from start->goal using parent pointers. Return None if goal unreachable."""
    if start == goal:
        return [start]
    if goal not in parent:
        return None

    path: List[Pos] = [goal]
    cur = goal
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path


def bfs_path(grid: Grid, start: Pos, goal: Pos) -> Tuple[Optional[List[Pos]], Set[Pos]]:
    """
    Queue-based BFS.
    Return (path, visited).
    - path is a list of positions from start to goal (inclusive), or None.
    - visited contains all explored/seen nodes.
    """
    q = deque([start])
    visited: Set[Pos] = {start}
    parent: Dict[Pos, Pos] = {}

    while q:
        cur = q.popleft()
        if cur == goal:
            return reconstruct_path(parent, start, goal), visited

        for nxt in neighbors(grid, cur):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = cur
            q.append(nxt)

    return None, visited


def dfs_path(grid: Grid, start: Pos, goal: Pos) -> Tuple[Optional[List[Pos]], Set[Pos]]:
    """
    Stack-based DFS (iterative, no recursion).
    Return (path, visited).
    """
    stack: List[Pos] = [start]
    visited: Set[Pos] = {start}
    parent: Dict[Pos, Pos] = {}

    while stack:
        cur = stack.pop()
        if cur == goal:
            return reconstruct_path(parent, start, goal), visited

        # reverse push order so traversal still follows U,R,D,L preference when popped
        for nxt in reversed(neighbors(grid, cur)):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = cur
            stack.append(nxt)

    return None, visited


def render(grid: Grid, path: Optional[List[Pos]] = None, visited: Optional[Set[Pos]] = None) -> str:
    """
    Render the grid as text.
    Overlay rules (recommended):
    - path tiles shown as '*'
    - visited tiles shown as '·' (middle dot) or '+'
    - preserve 'S' and 'G'
    """
    canvas: Grid = [row[:] for row in grid]
    visited = visited or set()

    for r, c in visited:
        if canvas[r][c] == ".":
            canvas[r][c] = "+"

    if path:
        for r, c in path:
            if canvas[r][c] == "." or canvas[r][c] == "+":
                canvas[r][c] = "*"

    return "\n".join("".join(row) for row in canvas)


def run_one(label: str, grid_text: str) -> None:
    grid, start, goal = parse_grid(grid_text)

    print("=" * 60)
    print(label)
    print("- Raw map")
    print(render(grid))

    path_bfs, visited_bfs = bfs_path(grid, start, goal)
    print("\n- BFS")
    print(f"found={path_bfs is not None} path_len={(len(path_bfs) if path_bfs else None)} visited={len(visited_bfs)}")
    print(render(grid, path=path_bfs, visited=visited_bfs))

    path_dfs, visited_dfs = dfs_path(grid, start, goal)
    print("\n- DFS")
    print(f"found={path_dfs is not None} path_len={(len(path_dfs) if path_dfs else None)} visited={len(visited_dfs)}")
    print(render(grid, path=path_dfs, visited=visited_dfs))


def parse_chase_grid(text: str) -> Tuple[Grid, Pos, Pos, Optional[Pos]]:
    """Parse a chase map containing P (player), M (monster), and optional G (exit)."""
    lines = [line for line in text.splitlines() if line.strip()]
    grid: Grid = [list(line) for line in lines]
    player: Optional[Pos] = None
    monster: Optional[Pos] = None
    goal: Optional[Pos] = None

    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == "P":
                player = (r, c)
                grid[r][c] = "."
            elif ch == "M":
                monster = (r, c)
                grid[r][c] = "."
            elif ch == "G":
                goal = (r, c)

    if player is None or monster is None:
        raise ValueError("Chase grid must include P and M")
    return grid, player, monster, goal


def step_toward(grid: Grid, start: Pos, goal: Pos, mode: str) -> Pos:
    """Return the next step from start toward goal using BFS or DFS, else stay put."""
    finder = bfs_path if mode.upper() == "BFS" else dfs_path
    path, _ = finder(grid, start, goal)
    if path and len(path) >= 2:
        return path[1]
    return start


def game_loop(mode: str = "BFS") -> None:
    """Tiny turn-based demo that shows how BFS/DFS monster behavior differs."""
    grid, player, monster, goal = parse_chase_grid(CHASE_MAP)

    print("\n" + "=" * 60)
    print(f"Monster Chase Demo (MODE={mode.upper()})")
    print("Controls: WASD then Enter, or Q to quit")

    while True:
        scene = [row[:] for row in grid]
        pr, pc = player
        mr, mc = monster
        scene[pr][pc] = "P"
        scene[mr][mc] = "M"
        print(render(scene))

        if player == monster:
            print("Monster reached you. You lose!")
            return
        if goal is not None and player == goal:
            print("You reached G. You win!")
            return

        cmd = input("Move (W/A/S/D, Q quit): ").strip().upper()
        if cmd == "Q":
            print("Game ended.")
            return

        move = {"W": (-1, 0), "A": (0, -1), "S": (1, 0), "D": (0, 1)}.get(cmd)
        if move is not None:
            nr, nc = player[0] + move[0], player[1] + move[1]
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != "#":
                player = (nr, nc)

        monster = step_toward(grid, monster, player, mode)


def main() -> None:
    run_one("Example Map 1", EXAMPLE_MAP_1)
    run_one("Example Map 2", EXAMPLE_MAP_2)

    print("\nTip: run game_loop('BFS') or game_loop('DFS') in a Python shell for the Monster Chase demo.")


if __name__ == "__main__":
    main()
