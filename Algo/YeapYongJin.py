#A* Search

import heapq
from allItem import StateKey, State, successors, is_goal_key, Metrics, heuristic_trips_remaining, run_single, run_all_extended, bfs_optimal_length
from data import TEST_CASES

ALGO_NAME = "A*"

def astar_solver(start: StateKey, metr: Metrics):
    tie = 0
    openh = []
    start_state = State(start, 0, None, None)
    heapq.heappush(openh, (heuristic_trips_remaining(start), 0, tie, start_state))
    gbest = {start: 0}
    closed = set()
    while openh:
        metr.track_frontier(len(openh))
        f, g, _, u = heapq.heappop(openh)
        if u.key in closed:
            continue
        closed.add(u.key)
        metr.bump()
        if is_goal_key(u.key):
            return u
        for v in successors(u, order="deterministic"):
            gv = v.g
            if (v.key not in gbest) or (gv < gbest[v.key]):
                gbest[v.key] = gv
                tie += 1
                fv = gv + heuristic_trips_remaining(v.key)
                heapq.heappush(openh, (fv, gv, tie, v))
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
            run_single(astar_solver, start, ALGO_NAME, animate=True, anim_speed=0.6)
        elif sel == "2":
            run_all_extended(astar_solver, TEST_CASES, algo_name=ALGO_NAME, optimal_by_case=optimal, repeats=1)
        elif sel == "0":
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
