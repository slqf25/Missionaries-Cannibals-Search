#simulated Annealing

import random
from allItem import StateKey, State, successors, is_goal_key, Metrics, run_single, run_all_extended, bfs_optimal_length
from data import TEST_CASES

ALGO_NAME = "Simulated Annealing "

def energy(k: StateKey) -> int:
    # remaining workload + small boat penalty to encourage boat on right
    return (k.m_left + k.c_left) + (0 if k.boat == 'R' else 1)

def accept_worse(deltaE: int, T: float) -> bool:
    # Linear-decay acceptance: P = max(0, 1 - deltaE / T)
    if T <= 1e-9:
        return False
    if deltaE <= 0:
        return True
    P = max(0.0, 1.0 - (deltaE / T))
    return random.random() < P

def sa_solver(start: StateKey, metr: Metrics, *, T0: float = 10.0, Tmin: float = 0.1, alpha: float = 0.995, k_max: int = 50000):
    cur = State(start, 0, None, None)
    best = cur
    T = T0
    k = 0
    while k < k_max and T > Tmin:
        metr.track_frontier(1)  # SA keeps O(1) states
        metr.bump()
        if is_goal_key(cur.key):
            return cur
        nbrs = successors(cur, order="random")
        if not nbrs:
            # small reheat
            T = min(T0, T * 1.2)
            k += 1
            continue
        nxt = random.choice(nbrs)
        dE = energy(nxt.key) - energy(cur.key)
        if dE <= 0 or accept_worse(dE, T):
            cur = nxt
            if energy(cur.key) < energy(best.key):
                best = cur
        T *= alpha
        k += 1
    if is_goal_key(best.key):
        return best
    return None

def main():
    optimal = {name: bfs_optimal_length(s) for name,s in TEST_CASES}
    while True:
        print(f"\n=== {ALGO_NAME} Menu ===")
        print("1) Choose ONE test case → animate + show metrics")
        print("2) Run ALL test cases (no animation) → summary table (best-of-20)")
        print("0) Exit")
        sel = input("Select: ").strip()
        if sel == "1":
            for i,(name, s) in enumerate(TEST_CASES,1):
                print(f"{i}) {name}: start={s}")
            idx = int(input("Pick one: ").strip()) - 1
            name, start = TEST_CASES[idx]
            run_single(lambda st, m: sa_solver(st, m), start, ALGO_NAME, animate=True, anim_speed=0.6)
        elif sel == "2":
            # SA 重复 20 次以体现成功率与最优差距更可靠
            run_all_extended(lambda st, m: sa_solver(st, m), TEST_CASES, algo_name=ALGO_NAME, optimal_by_case=optimal, repeats=20)
        elif sel == "0":
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
