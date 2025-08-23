# mc_shared.py
# Core datatypes, validation, successor generation, rendering, animation, and common runners.

import time
from dataclasses import dataclass
from collections import namedtuple
from data import TOTAL_M, TOTAL_C, BOAT_CAPACITY, TESTS, get_test_by_index

ANIMATION_DELAY = 0.8  # fixed animation speed

@dataclass(frozen=True)
class StateKey:
    m_left: int
    c_left: int
    boat: str  # 'L' or 'R'

class State:
    __slots__ = ("key", "g", "parent", "last_move")
    def __init__(self, m_left, c_left, boat, g=0, parent=None, last_move=None):
        self.key = StateKey(m_left, c_left, boat)
        self.g = g
        self.parent = parent
        self.last_move = last_move  # (m, c, "L→R"/"R→L")

def is_valid_key(k: StateKey) -> bool:
    if not (0 <= k.m_left <= TOTAL_M and 0 <= k.c_left <= TOTAL_C):
        return False
    m_r, c_r = TOTAL_M - k.m_left, TOTAL_C - k.c_left
    if k.m_left > 0 and k.c_left > k.m_left:  # left bank unsafe
        return False
    if m_r > 0 and c_r > m_r:                 # right bank unsafe
        return False
    return True

def is_goal_key(k: StateKey) -> bool:
    return k.m_left == 0 and k.c_left == 0 and k.boat == 'R'

# Allowed boat moves: 1 or 2 total people
MOVES = [(1,0), (2,0), (0,1), (0,2), (1,1)]

def successors(s: State):
    out = []
    for m, c in MOVES:
        if 1 <= m + c <= BOAT_CAPACITY:
            if s.key.boat == 'L':
                k2 = StateKey(s.key.m_left - m, s.key.c_left - c, 'R')
                mv = (m, c, "L→R")
            else:
                k2 = StateKey(s.key.m_left + m, s.key.c_left + c, 'L')
                mv = (m, c, "R→L")
            if is_valid_key(k2):
                out.append(State(k2.m_left, k2.c_left, k2.boat, s.g + 1, s, mv))
    out.sort(key=lambda v: (v.key.m_left, v.key.c_left, v.key.boat))  # deterministic
    return out

# Admissible heuristic for A*: minimum trips ≈ ceil((m+c)/2)
def h(k: StateKey) -> int:
    return (k.m_left + k.c_left + 1) // 2

def render_frame(k: StateKey):
    m_r, c_r = TOTAL_M - k.m_left, TOTAL_C - k.c_left
    boat_L = "🚣" if k.boat == 'L' else "  "
    boat_R = "🚣" if k.boat == 'R' else "  "
    return f"[M:{k.m_left} C:{k.c_left}] {boat_L} {'~'*22} {boat_R} [M:{m_r} C:{c_r}]"

def play_animation(path_keys):
    print("\nAnimation:")
    for k in path_keys:
        print(render_frame(k))
        time.sleep(ANIMATION_DELAY)
    print("")

class Metrics:
    def __init__(self):
        self.nodes_expanded = 0
        self.max_frontier_size = 0
    def bump(self, k=1):
        self.nodes_expanded += k
    def track_frontier(self, size):
        if size > self.max_frontier_size:
            self.max_frontier_size = size

Result = namedtuple("Result", "case_idx case_name path_len secs expanded frontier success")

def print_table(rows, title):
    print(f"\n{title}")
    print("+----+----------------------+------------+----------+---------------+------------------+")
    print("| #  | Case Name            | Path Len   | Time(s)  | Nodes Expanded| Max Frontier Size|")
    print("+----+----------------------+------------+----------+---------------+------------------+")
    for r in rows:
        print(f"| {r.case_idx:>2} | {r.case_name[:20]:<20} | {r.path_len:>10} | {r.secs:>8.5f} | "
              f"{r.expanded:>13} | {r.frontier:>16} |")
    print("+----+----------------------+------------+----------+---------------+------------------+\n")

def run_single(solver_fn, start_key, algo_name:str, animate=True):
    metr = Metrics()
    t0 = time.perf_counter()
    path = solver_fn(start_key, metr)
    t1 = time.perf_counter()
    success = bool(path)
    if animate and path:
        play_animation(path)
    print(f"Result: {'Goal reached ✅' if success else 'Not found/Not guaranteed ❗'}")
    print(f"Path length: {len(path) if success else 0}")
    print(f"Time(s): {t1 - t0:.6f}")
    print(f"Nodes expanded: {metr.nodes_expanded}")
    print(f"Max frontier size: {metr.max_frontier_size}\n")
    return success, (len(path) if success else 0), (t1 - t0), metr.nodes_expanded, metr.max_frontier_size

def run_all(solver_fn, algo_name:str):
    rows = []
    for idx in range(1, len(TESTS) + 1):
        case_name, cfg = get_test_by_index(idx)
        print(f"Running {algo_name} on case {idx}: {case_name}  start={cfg}")
        start_key = StateKey(cfg[0], cfg[1], cfg[2])
        ok, plen, secs, expanded, frontier = run_single(solver_fn, start_key, algo_name, animate=False)
        rows.append(Result(idx, case_name, plen, secs, expanded, frontier, ok))
    print_table(rows, f"{algo_name} — Summary Across {len(rows)} Cases")
