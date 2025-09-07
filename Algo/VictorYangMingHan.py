#Depth-First Search

from allItem import StateKey, State, successors, is_goal_key, Metrics, run_single, run_all_extended, bfs_optimal_length
from data import TEST_CASES

ALGO_NAME = "DFS"

def dfs_solver(start: StateKey, metr: Metrics):
    stack = [State(start, 0, None, None)]
    visited = set()
    while stack:
        metr.track_frontier(len(stack))
        u = stack.pop()
        if u.key in visited:
            continue
        visited.add(u.key)
        metr.bump()
        if is_goal_key(u.key):
            return u
        # randomize successors to reveal non-optimality occasionally
        for v in successors(u, order="random"):
            if v.key not in visited:
                stack.append(v)
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
            run_single(dfs_solver, start, ALGO_NAME, animate=True, anim_speed=0.6)
        elif sel == "2":
            run_all_extended(dfs_solver, TEST_CASES, algo_name=ALGO_NAME, optimal_by_case=optimal, repeats=1)
        elif sel == "0":
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
