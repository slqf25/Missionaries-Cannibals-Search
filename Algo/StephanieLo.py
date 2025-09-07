#Breadth-First Search

from collections import deque
from allItem import StateKey, State, successors, is_goal_key, Metrics, run_single, run_all_extended, optimal_length_baseline
from data import TEST_CASES

ALGO_NAME = "BFS"

def bfs_solver(start: StateKey, metr: Metrics):
    q = deque()
    q.append(State(start, 0, None, None))
    visited = set([start])
    while q:
        metr.track_frontier(len(q))
        u = q.popleft()
        metr.bump()
        if is_goal_key(u.key):
            return u
        for v in successors(u, order="deterministic"):
            if v.key not in visited:
                visited.add(v.key)
                q.append(v)
    return None

def main():
    # precompute optimal lengths for gaps
    optimal = {name: optimal_length_baseline(s) for name,s in TEST_CASES}
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
            run_single(bfs_solver, start, ALGO_NAME, animate=True, anim_speed=0.6)
        elif sel == "2":
            run_all_extended(bfs_solver, TEST_CASES, algo_name=ALGO_NAME, optimal_by_case=optimal, repeats=1)
        elif sel == "0":
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
