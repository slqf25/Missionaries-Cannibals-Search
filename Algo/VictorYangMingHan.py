#Depth-First Search

from data import list_tests, get_test_by_index
from allItem import StateKey, State, successors, is_goal_key, run_single, run_all

def dfs(start_key: StateKey, metr):
    stack = [State(start_key.m_left, start_key.c_left, start_key.boat)]
    visited = set()
    while stack:
        metr.track_frontier(len(stack))
        u = stack.pop()
        if u.key in visited:
            continue
        visited.add(u.key)
        metr.bump()
        if is_goal_key(u.key):
            path = []
            s = u
            while s:
                path.append(s.key)
                s = s.parent
            return list(reversed(path))
        succ = successors(u)
        for v in reversed(succ):  # LIFO
            if v.key not in visited:
                stack.append(v)
    return []

def main():
    algo_name = "DFS"
    solver_fn = dfs

    print(f"=== Missionaries & Cannibals — {algo_name} ===")
    while True:
        print("\nMenu:")
        print(" 1) Visualize ONE test case")
        print(" 2) Run ONE test case (no animation)")
        print(" 3) Run ALL test cases and show comparison table")
        print(" 0) Exit")
        choice = input("Select: ").strip()

        if choice == "0":
            print("Goodbye.")
            break
        elif choice in ("1", "2"):
            print("\nAvailable test cases:")
            list_tests()
            try:
                idx = int(input("Pick a case (1-10): "))
                case_name, cfg = get_test_by_index(idx)
            except Exception:
                print("Invalid selection.\n")
                continue
            start_key = StateKey(cfg[0], cfg[1], cfg[2])
            run_single(solver_fn, start_key, algo_name, animate=(choice == "1"))
        elif choice == "3":
            run_all(solver_fn, algo_name)
        else:
            print("Invalid selection.\n")

if __name__ == "__main__":
    main()
