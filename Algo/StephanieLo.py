#Breadth-First Search

# bfs_mc.py
from collections import deque
from data import list_tests, get_test_by_index
from allItem import StateKey, State, successors, is_goal_key, run_single, run_all_extended

def bfs(start_key: StateKey, metr):
    q = deque([State(start_key.m_left, start_key.c_left, start_key.boat)])
    visited = set()
    while q:
        metr.track_frontier(len(q))
        u = q.popleft()
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
        for v in successors(u):
            if v.key not in visited:
                q.append(v)
    return []

def main():
    algo_name = "BFS"
    print(f"=== Missionaries & Cannibals — {algo_name} ===")
    while True:
        print("\nMenu:")
        print(" 1. Select 1 data set to test")
        print(" 2. Overall report generation")
        print(" 0. Exit")
        choice = input("Select: ").strip()

        if choice == "0":
            print("Goodbye.")
            break
        elif choice == "1":
            print("\nAvailable test cases:")
            list_tests()
            try:
                idx = int(input("Pick a case (1-10): "))
                case_name, cfg = get_test_by_index(idx)
            except Exception:
                print("Invalid selection.\n")
                continue
            start_key = StateKey(cfg[0], cfg[1], cfg[2])
            run_single(bfs, start_key, algo_name, animate=True, case_idx=idx, case_name=case_name)
        elif choice == "2":
            run_all_extended(bfs, algo_name)
        else:
            print("Invalid selection.\n")

if __name__ == "__main__":
    main()

