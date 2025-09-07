import time
import math
import random
import tracemalloc
import os
import heapq
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set

# -------- ANSI Color Helpers --------
USE_COLOR = True  # set False to disable coloring
def _c(text, code):
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"
CLR_M = "97"     # bright white for Missionary
CLR_C = "91"     # red for Cannibal
CLR_BOAT = "94"  # blue for boat
CLR_WAVE = "36"  # cyan for river
CLR_BANK = "90"  # dim for bank labels

# -------- Problem Constants --------
TOTAL_M = 3
TOTAL_C = 3
BOAT_CAPACITY = 2

# legal move patterns: (moved_missionaries, moved_cannibals)
MOVES = [(2,0),(0,2),(1,0),(0,1),(1,1)]

# -------- State Definition --------
@dataclass(frozen=True)
class StateKey:
    m_left: int
    c_left: int
    boat: str  # 'L' or 'R'

@dataclass
class State:
    key: StateKey
    g: int = 0
    parent: Optional["State"] = None
    last_move: Optional[Tuple[int,int,str]] = None  # (m,c,"L→R" or "R→L")

# -------- Validity & Goal --------
def is_valid_key(k: StateKey) -> bool:
    # bounds
    if not (0 <= k.m_left <= TOTAL_M and 0 <= k.c_left <= TOTAL_C):
        return False
    if k.boat not in ('L','R'):
        return False
    # compute right bank
    m_right = TOTAL_M - k.m_left
    c_right = TOTAL_C - k.c_left
    # safety: missionaries not outnumbered where present
    if k.m_left > 0 and k.c_left > k.m_left:
        return False
    if m_right > 0 and c_right > m_right:
        return False
    return True

def is_goal_key(k: StateKey) -> bool:
    return k.m_left == 0 and k.c_left == 0 and k.boat == 'R'

# -------- Successor Generation --------
def successors(s: State, *, order: str = "deterministic") -> List[State]:
    out: List[State] = []
    for m,c in MOVES:
        if 1 <= m + c <= BOAT_CAPACITY:
            if s.key.boat == 'L':
                k2 = StateKey(s.key.m_left - m, s.key.c_left - c, 'R')
                mv = (m, c, "L→R")
            else:
                k2 = StateKey(s.key.m_left + m, s.key.c_left + c, 'L')
                mv = (m, c, "R→L")
            if is_valid_key(k2):
                out.append(State(k2, s.g + 1, s, mv))
    if order == "deterministic":
        out.sort(key=lambda v: (v.key.m_left, v.key.c_left, v.key.boat))
    elif order == "random":
        random.shuffle(out)
    return out

# -------- Heuristic (admissible & consistent) --------
def heuristic_trips_remaining(k: StateKey) -> int:
    # ceil((M_left + C_left)/2)
    return (k.m_left + k.c_left + 1) // 2

# -------- Metrics --------
class Metrics:
    def __init__(self):
        self.expanded = 0
        self.max_frontier = 0
        self.peak_mem_kb = 0
    def bump(self):
        self.expanded += 1
    def track_frontier(self, n: int):
        if n > self.max_frontier:
            self.max_frontier = n
    def track_memory(self):
        cur, peak = tracemalloc.get_traced_memory()
        pk = peak // 1024
        if pk > self.peak_mem_kb:
            self.peak_mem_kb = pk

# -------- ASCII Rendering Helpers --------
def _render_banks(k: StateKey) -> Tuple[str, str]:
    left_people = _c("M"*k.m_left, CLR_M) + (" " if k.m_left and k.c_left else "") + _c("C"*k.c_left, CLR_C)
    right_people = _c("M"*(TOTAL_M - k.m_left), CLR_M) + (" " if (TOTAL_M-k.m_left) and (TOTAL_C-k.c_left) else "") + _c("C"*(TOTAL_C - k.c_left), CLR_C)
    left = _c("L | ", CLR_BANK) + left_people
    right = right_people + _c(" | R", CLR_BANK)
    return left, right

def _render_scene(k: StateKey, boat_pos: int, m_on_boat: int, c_on_boat: int, width: int = 28) -> str:
    waves_raw = "~"*width
    boat_load = ("M"*m_on_boat + "C"*c_on_boat) or " "
    boat = _c(f"[{boat_load:2s}]", CLR_BOAT)
    boat_pos = max(0, min(len(waves_raw)-3, boat_pos))
    river_colored = _c(waves_raw[:boat_pos], CLR_WAVE) + boat + _c(waves_raw[boat_pos+3:], CLR_WAVE)
    left, right = _render_banks(k)
    return f"{left}\n{river_colored}\n{right}\n"

# -------- Animation (ASCII river + moving boat) --------
def play_animation(goal_state: Optional[State], *, speed: float = 0.6):
    if goal_state is None:
        print("\nNo solution to animate.\n")
        return
    # Reconstruct path
    path = []
    s = goal_state
    while s is not None:
        path.append(s)
        s = s.parent
    path.reverse()

    print("\n--- Animation (ASCII river with moving boat) ---")
    width = 28
    for i, st in enumerate(path):
        k = st.key
        m_on_boat, c_on_boat = (0, 0)
        direction = None
        if st.last_move:
            m_on_boat, c_on_boat, direction = st.last_move

        # travel phase between previous state and current state
        if i > 0 and direction:
            if direction == "L→R":
                for x in range(0, width-2, 3):
                    frame = _render_scene(StateKey(path[i-1].key.m_left - m_on_boat, path[i-1].key.c_left - c_on_boat, 'R'), x, m_on_boat, c_on_boat, width)
                    print(frame, end="")
                    time.sleep(max(0.04, speed/7))
                    print("\033[3A", end="")  # move cursor up to overwrite 3 lines
            else:
                for x in range(width-3, -1, -3):
                    frame = _render_scene(StateKey(path[i-1].key.m_left + m_on_boat, path[i-1].key.c_left + c_on_boat, 'L'), x, m_on_boat, c_on_boat, width)
                    print(frame, end="")
                    time.sleep(max(0.04, speed/7))
                    print("\033[3A", end="")

        # landed frame
        frame = _render_scene(k, 0 if k.boat=='L' else width-3, 0, 0, width)
        print(frame, end="")
        mR = TOTAL_M - k.m_left
        cR = TOTAL_C - k.c_left
        step_info = f"Step {i:02d}  move: {m_on_boat}M {c_on_boat}C {direction or ''}    Left(M={k.m_left},C={k.c_left})  Right(M={mR},C={cR})"
        print(step_info + "\n")
        time.sleep(speed)
    print("--- End Animation ---\n")

# -------- Path Reconstruction --------
def reconstruct_path(goal: Optional[State]) -> List[StateKey]:
    if goal is None:
        return []
    seq = []
    s = goal
    while s:
        seq.append(s.key)
        s = s.parent
    seq.reverse()
    return seq


def optimal_length_baseline(start: StateKey) -> Optional[int]:
    """Compute the optimal boat-trip length from start to goal using A*.
    Uses h(n)=ceil((M_left+C_left)/2), which is admissible & consistent.
    This function is algorithm-neutral and used only to compute the ground-truth
    optimal length for reporting the Optimality Gap."""
    start_state = State(start, 0, None, None)
    openh = []
    tie = 0
    def h(k: StateKey) -> int:
        return (k.m_left + k.c_left + 1) // 2  # same as heuristic_trips_remaining
    heapq.heappush(openh, (h(start), 0, tie, start_state))
    gbest: Dict[StateKey, int] = {start: 0}
    closed: Set[StateKey] = set()
    while openh:
        f, g, _, u = heapq.heappop(openh)
        if u.key in closed:
            continue
        closed.add(u.key)
        if is_goal_key(u.key):
            return u.g
        for v in successors(u, order="deterministic"):
            gv = v.g  # each move costs 1 boat trip
            if (v.key not in gbest) or (gv < gbest[v.key]):
                gbest[v.key] = gv
                tie += 1
                heapq.heappush(openh, (gv + h(v.key), gv, tie, v))
    return None

# -------- Runner Utilities --------
def run_single(solver_fn, start: StateKey, algo_name: str, *, animate: bool = True, anim_speed: float = 0.6):
    metr = Metrics()
    # time and memory
    tracemalloc.start()
    t0 = time.perf_counter()
    goal = solver_fn(start, metr)
    t1 = time.perf_counter()
    metr.track_memory()
    tracemalloc.stop()
    # results
    if goal:
        path = reconstruct_path(goal)
        path_len = max(0, len(path) - 1)
        success = True
    else:
        path_len = None
        success = False
    # show
    print(f"\n[{algo_name}] Single-case result")
    print("Start:", start, "Goal:", (0,0,'R'))
    print(f"Success: {success}  PathLen(boat trips): {path_len}  Time(s): {t1 - t0:.6f}  Expanded: {metr.expanded}  MaxFrontier: {metr.max_frontier}  PeakKB: {metr.peak_mem_kb}")
    if animate:
        play_animation(goal, speed=anim_speed)
    return {"success": success, "path_len": path_len, "time": t1 - t0, "expanded": metr.expanded, "frontier": metr.max_frontier, "peak_kb": metr.peak_mem_kb}

def run_all_extended(solver_fn, cases: List[Tuple[str, StateKey]], *, algo_name: str, optimal_by_case: Dict[str, Optional[int]], repeats:int=1):
    rows = []
    print(f"\n[{algo_name}] Run ALL test cases (repeats={repeats})")
    for name, start in cases:
        best = None
        success_count = 0
        accum_time = 0.0
        accum_expanded = 0
        accum_frontier = 0
        accum_peak = 0
        for r in range(repeats):
            res = run_single(solver_fn, start, algo_name, animate=False)
            if res["success"]:
                success_count += 1
                if (best is None) or (res["path_len"] < best["path_len"]):
                    best = res
            accum_time += res["time"]
            accum_expanded += res["expanded"]
            accum_frontier += res["frontier"]
            accum_peak += res["peak_kb"]
        avg_time = accum_time / repeats
        avg_exp = accum_expanded // repeats
        avg_frontier = accum_frontier // repeats
        avg_peak = accum_peak // repeats
        opt = optimal_by_case.get(name)
        gap = None
        if best and opt is not None:
            gap = best["path_len"] - opt
        rows.append((name, best["success"] if best else False, best["path_len"] if best else None, avg_time, avg_exp, avg_frontier, avg_peak, gap, success_count, repeats))
    # print table
    print("\nCase\tSucc\tPath\tTime(s)\tExpanded\tFrontier\tPeakKB\tGap\tSuccessRate")
    for (name, succ, plen, at, ae, af, ap, gap, sc, rep) in rows:
        rate = f"{sc}/{rep}"
        print(f"{name}\t{succ}\t{plen}\t{at:.6f}\t{ae}\t\t{af}\t\t{ap}\t{gap}\t{rate}")
    return rows
