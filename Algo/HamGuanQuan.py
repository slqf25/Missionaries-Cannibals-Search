#simulated Annealing

import random, math
from data import list_tests, get_test_by_index
from allItem import StateKey, State, successors, is_goal_key, run_single, run_all

SA_MAX_ITERS = 50000
SA_T_START, SA_T_END = 5.0, 0.002
SA_REPEATS = 20

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

def sa_best_of_repeats(start_key: StateKey, metr):
    random.seed()
    best = []
    for _ in range(SA_REPEATS):
        path = sa_single(start_key, metr)
        if path and is_goal_key(path[-1]):
            return path
        if len(path) > len(best):
            best = path
    return best if best and is_goal_key(best[-1]) else []

def main():
    algo_name = "Simulated Annealing"
    solver_fn = sa_best_of_repeats

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
