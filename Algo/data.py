# Shared test cases for Missionaries & Cannibals

TOTAL_M = 3
TOTAL_C = 3
BOAT_CAPACITY = 2

# Named test cases (you can rename or add more if needed)
TESTS = [
    ("Classic default",     (3, 3, 'L')),
    ("Left heavy M",        (3, 2, 'L')),
    ("Left heavy C",        (2, 3, 'L')),
    ("Balanced small",      (2, 2, 'L')),
    ("Few C",               (3, 1, 'L')),
    ("Few M",               (1, 3, 'L')),
    ("Only M left",         (3, 0, 'L')),
    ("Only C left",         (0, 3, 'L')),
    ("Near goal mix A",     (2, 1, 'L')),
    ("Near goal mix B",     (1, 2, 'L')),
]

def list_tests():
    for i, (name, cfg) in enumerate(TESTS, 1):
        print(f"{i}. {name:<18} start={cfg}  goal=(0,0,'R')")

def get_test_by_index(idx: int):
    name, cfg = TESTS[idx - 1]
    return name, cfg
