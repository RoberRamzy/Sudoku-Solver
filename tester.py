import time
import board as BM


# -----------------------------
# METRICS CONTAINER
# -----------------------------
class Metrics:
    def __init__(self):
        self.arc_checks = 0
        self.domain_reductions = 0
        self.queue_pushes = 0
        self.queue_pops = 0
        self.bt_calls = 0
        self.ac3_time = 0
        self.bt_time = 0


# -----------------------------
# INSTRUMENTED REVISE
# -----------------------------
def revise_instrumented(board, xi, xj, metrics):
    revised = False

    for x in list(board.domains[xi]):
        metrics.arc_checks += 1

        if all(x == y for y in board.domains[xj]):
            board.domains[xi].remove(x)
            metrics.domain_reductions += 1
            revised = True

    return revised


# -----------------------------
# INSTRUMENTED AC3
# -----------------------------
def ac3_instrumented(board, metrics):
    queue = []

    for r in range(9):
        for c in range(9):
            xi = (r, c)
            for xj in board.get_neighbors(r, c):
                queue.append((xi, xj))
                metrics.queue_pushes += 1

    start = time.perf_counter()

    while queue:
        xi, xj = queue.pop(0)
        metrics.queue_pops += 1

        if revise_instrumented(board, xi, xj, metrics):

            if len(board.domains[xi]) == 0:
                return False

            for xk in board.get_neighbors(*xi):
                if xk != xj:
                    queue.append((xk, xi))
                    metrics.queue_pushes += 1

    metrics.ac3_time = (time.perf_counter() - start) * 1000
    return True


# -----------------------------
# INSTRUMENTED BACKTRACKING
# -----------------------------
def backtrack_instrumented(board, metrics):
    metrics.bt_calls += 1

    cell = board.find_unassigned()
    if not cell:
        return True

    r, c = cell

    for val in list(board.domains[(r, c)]):
        if board.is_valid(r, c, val):
            board.grid[r][c] = val

            if backtrack_instrumented(board, metrics):
                return True

            board.grid[r][c] = 0

    return False


# -----------------------------
# FULL PIPELINE TEST
# -----------------------------
def run_solver_with_metrics(grid):
    b = BM.Board()

    # Load puzzle
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                b.set_cell(r, c, grid[r][c], True)

    b.initial_reduction()

    metrics = Metrics()

    # --- AC3 ---
    ac3_success = ac3_instrumented(b, metrics)

    # --- Commit singleton domains ---
    changed = True
    while changed:
        changed = False
        for r in range(9):
            for c in range(9):
                if b.grid[r][c] == 0 and len(b.domains[(r, c)]) == 1:
                    val = list(b.domains[(r, c)])[0]
                    b.set_cell(r, c, val)
                    changed = True

    # --- Backtracking ---
    start_bt = time.perf_counter()
    solved = backtrack_instrumented(b, metrics)
    metrics.bt_time = (time.perf_counter() - start_bt) * 1000

    return b, metrics, solved, ac3_success


# -----------------------------
# SAMPLE TEST CASE
# -----------------------------
def test_hard_sudoku():
    grid_hard = [
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,3,0,8,5],
        [0,0,1,0,2,0,0,0,0],
        [0,0,0,5,0,7,0,0,0],
        [0,0,4,0,0,0,1,0,0],
        [0,9,0,0,0,0,0,0,0],
        [5,0,0,0,0,0,0,7,3],
        [0,0,2,0,1,0,0,0,0],
        [0,0,0,0,4,0,0,0,9],
    ]

    board, metrics, solved, ac3_ok = run_solver_with_metrics(grid_hard)

    print("\n=== METRICS ===")
    print("Solved:", solved)
    print("AC3 success:", ac3_ok)
    print("AC3 time (ms):", round(metrics.ac3_time, 2))
    print("BT time (ms):", round(metrics.bt_time, 2))
    print("Arc checks:", metrics.arc_checks)
    print("Domain reductions:", metrics.domain_reductions)
    print("Queue pushes:", metrics.queue_pushes)
    print("Queue pops:", metrics.queue_pops)
    print("Backtracking calls:", metrics.bt_calls)

    print("\n=== SOLUTION ===")
    for row in board.grid:
        print(row)

def test_medium_sudoku():
    grid_medium =  [[0, 2, 0, 6, 0, 8, 0, 0, 0],
                    [5, 8, 0, 0, 0, 9, 7, 0, 0],
                    [0, 0, 0, 0, 4, 0, 0, 0, 0],
                    [3, 7, 0, 0, 0, 0, 5, 0, 0],
                    [6, 0, 0, 0, 0, 0, 0, 0, 4],
                    [0, 0, 8, 0, 0, 0, 0, 1, 3],
                    [0, 0, 0, 0, 2, 0, 0, 0, 0],
                    [0, 0, 9, 8, 0, 0, 0, 3, 6],
                    [0, 0, 0, 3, 0, 6, 0, 9, 0]]

    board, metrics, solved, ac3_ok = run_solver_with_metrics(grid_medium)

    print("\n=== METRICS ===")
    print("Solved:", solved)
    print("AC3 success:", ac3_ok)
    print("AC3 time (ms):", round(metrics.ac3_time, 2))
    print("BT time (ms):", round(metrics.bt_time, 2))
    print("Arc checks:", metrics.arc_checks)
    print("Domain reductions:", metrics.domain_reductions)
    print("Queue pushes:", metrics.queue_pushes)
    print("Queue pops:", metrics.queue_pops)
    print("Backtracking calls:", metrics.bt_calls)

    print("\n=== SOLUTION ===")
    for row in board.grid:
        print(row)

def test_ez_sudoku():
    grid_easy = [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],

        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],

        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9],
    ]

    board, metrics, solved, ac3_ok = run_solver_with_metrics(grid_easy)

    print("\n=== METRICS ===")
    print("Solved:", solved)
    print("AC3 success:", ac3_ok)
    print("AC3 time (ms):", round(metrics.ac3_time, 2))
    print("BT time (ms):", round(metrics.bt_time, 2))
    print("Arc checks:", metrics.arc_checks)
    print("Domain reductions:", metrics.domain_reductions)
    print("Queue pushes:", metrics.queue_pushes)
    print("Queue pops:", metrics.queue_pops)
    print("Backtracking calls:", metrics.bt_calls)

    print("\n=== SOLUTION ===")
    for row in board.grid:
        print(row)


if __name__ == "__main__":
    test_hard_sudoku()