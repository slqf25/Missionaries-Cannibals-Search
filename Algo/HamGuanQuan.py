#simulated Annealing

import random, math
from data import list_tests, get_test_by_index
from allItem import StateKey, State, successors, is_goal_key, run_single, run_all_extended

SA_MAX_ITERS = 50000
SA_T_START, SA_T_END = 5.0, 0.002
SA_REPEATS_DEFAULT = 20

def sa_cost(k: StateKey):
    return k.m_left + k.c_left + (0 if k.boat == 'R' else 1)

def schedule(tfrac):
    return SA_T_START * ((SA_T_END / SA_T_START) ** tfrac)

def sa_single(start_key: StateKey, metr):
    cur = State(start_key.m_left, start_key.c_left, start_key.boat)
    best = cur
    for it in range(1, SA_MAX_ITERS + 1):
        metr.bump()
        if is_goal_key(cur.key):
            path = []
            s = cur
            while s:
                path.append(s.key)
                s = s.parent
            return list(reversed(path))
        T = schedule(it / SA_MAX_ITERS)
        nbrs = successors(cur)
        metr.track_frontier(len(nbrs))
        if not nbrs:
            cur = State(start_key.m_left, start_key.c_left, start_key.boat)
            continue
        nxt = random.choice(nbrs)
        d = sa_cost(nxt.key) - sa_cost(cur.key)
        if d <= 0 or random.random() < math.exp(-d / max(T, 1e-12)):
            cur = nxt
        if sa_cost(cur.key) < sa_cost(best.key):
            best = cur
    path = []
    s = best
    while s:
        path.append(s.key)
        s = s.parent
    path = list(reversed(path))
    return path if path and is_goal_key(path[-1]) else []

def sa_best_of_repeats(start_key: StateKey, metr, repeats:int=1):
    random.seed()
    best = []
    for _ in range(repeats):
        path = sa_single(start_key, metr)
        if path and is_goal_key(path[-1]):
            return path
        if len(path) > len(best):
            best = path
    return best if best and is_goal_key(best[-1]) else []

def main():
    algo_name = "Simulated Annealing"
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
            def solver(start_key, metr): return sa_single(start_key, metr)
            run_single(solver, start_key, algo_name, animate=True, case_idx=idx, case_name=case_name)
        elif choice == "2":
            def solver_repeat(start_key, metr): return sa_best_of_repeats(start_key, metr, repeats=SA_REPEATS_DEFAULT)
            run_all_extended(solver_repeat, algo_name, sa_repeats=SA_REPEATS_DEFAULT)
        else:
            print("Invalid selection.\n")

if __name__ == "__main__":
    main()
