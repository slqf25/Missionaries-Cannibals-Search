#A* Search

import heapq
from data import list_tests, get_test_by_index
from allItem import StateKey, State, successors, is_goal_key, h, run_single, run_all_extended

def astar(start_key: StateKey, metr):
    start = State(start_key.m_left, start_key.c_left, start_key.boat)
    openh, tie = [], 0
    gbest = {start.key: 0}
    heapq.heappush(openh, (h(start.key), 0, tie, start))  # (f, g, tie, node)
    while openh:
        metr.track_frontier(len(openh))
        _, _, _, u = heapq.heappop(openh)
        metr.bump()
        if is_goal_key(u.key):
            path = []
            s = u
            while s:
                path.append(s.key)
                s = s.parent
            return list(reversed(path))
        for v in successors(u):
            g2 = u.g + 1
            if g2 < gbest.get(v.key, 10**9):
                gbest[v.key] = g2
                tie += 1
                heapq.heappush(openh, (g2 + h(v.key), g2, tie, v))
    return []

def main():
    algo_name = "A*"
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
            run_single(astar, start_key, algo_name, animate=True, case_idx=idx, case_name=case_name)
        elif choice == "2":
            run_all_extended(astar, algo_name)
        else:
            print("Invalid selection.\n")

if __name__ == "__main__":
    main()
