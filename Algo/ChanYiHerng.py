# Greedy Best-First Search

import heapq
from allItem import StateKey, State, successors, is_goal_key, Metrics, heuristic_trips_remaining, run_single, run_all_extended, bfs_optimal_length
from data import TEST_CASES

ALGO_NAME = "Greedy Best-First"

def greedy_solver(start: StateKey, metr: Metrics):
    tie = 0
    pq = []
    start_state = State(start, 0, None, None)
    heapq.heappush(pq, (heuristic_trips_remaining(start), tie, start_state))
    visited = set()
    while pq:
        metr.track_frontier(len(pq))
        h, _, u = heapq.heappop(pq)
        if u.key in visited:
            continue
        visited.add(u.key)
        metr.bump()
        if is_goal_key(u.key):
            return u
        for v in successors(u, order="random"):
            if v.key not in visited:
                tie += 1
                heapq.heappush(pq, (heuristic_trips_remaining(v.key), tie, v))
    return None

def main():
    optimal = {name: bfs_optimal_length(s) for name,s in TEST_CASES}
    while True:
        print(f"\n=== {ALGO_NAME} Menu ===")
        print("1) Choose ONE test case → animate + show metrics")
        print("2) Run ALL test cases (no animation) → summary table")
        print("0) Exit")
        sel = input("Select: ").strip()
        if sel == "1":
            for i,(name, s) in enumerate(TEST_CASES,1):
                print(f"{i}) {name}: start={s}")
            idx = int(input("Pick one: ").strip()) - 1
            name, start = TEST_CASES[idx]
            run_single(greedy_solver, start, ALGO_NAME, animate=True, anim_speed=0.6)
        elif sel == "2":
            run_all_extended(greedy_solver, TEST_CASES, algo_name=ALGO_NAME, optimal_by_case=optimal, repeats=1)
        elif sel == "0":
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
