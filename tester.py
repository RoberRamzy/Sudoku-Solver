import time
from board import Board

def reset_metrics(board):
    board.metrics.arc_checks = 0
    board.metrics.domain_reductions = 0
    board.metrics.queue_pushes = 0
    board.metrics.queue_pops = 0
    board.metrics.bt_calls = 0
    board.metrics.ac3_time = 0
    board.metrics.bt_time = 0


# -----------------------------
# RUN SINGLE TEST
# -----------------------------
def run_test(name, grid):
    print("\n" + "=" * 60)
    print(f"TEST: {name}")
    print("=" * 60)

    board = Board()
    reset_metrics(board)

    # Load puzzle
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                board.set_cell(r, c, grid[r][c], True)

    board.initial_reduction()

    # ---------------- AC3 ----------------
    start = time.perf_counter()
    ac3_ok = board.ac3()   # uses internal metrics now
    board.metrics.ac3_time = (time.perf_counter() - start) * 1000

    # ---------------- BACKTRACKING ----------------
    start = time.perf_counter()
    solved = board.backtrack_fc(board.metrics)
    board.metrics.bt_time = (time.perf_counter() - start) * 1000

    # ---------------- RESULTS ----------------
    print("\n--- RESULT ---")
    print("Solved:", solved)
    print("AC3 success:", ac3_ok)

    print("\n--- TIMING ---")
    print("AC3 time (ms):", round(board.metrics.ac3_time, 2))
    print("BT time (ms):", round(board.metrics.bt_time, 2))

    print("\n--- METRICS ---")
    print("Arc checks:", board.metrics.arc_checks)
    print("Domain reductions:", board.metrics.domain_reductions)
    print("Queue pushes:", board.metrics.queue_pushes)
    print("Queue pops:", board.metrics.queue_pops)
    print("Backtracking calls:", board.metrics.bt_calls)

    print("\n--- SOLUTION ---")
    for row in board.grid:
        print(row)


# -----------------------------
# TEST CASES
# -----------------------------
grid_easy = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9],
]

grid_medium = [
    [0,2,0,6,0,8,0,0,0],
    [5,8,0,0,0,9,7,0,0],
    [0,0,0,0,4,0,0,0,0],
    [3,7,0,0,0,0,5,0,0],
    [6,0,0,0,0,0,0,0,4],
    [0,0,8,0,0,0,0,1,3],
    [0,0,0,0,2,0,0,0,0],
    [0,0,9,8,0,0,0,3,6],
    [0,0,0,3,0,6,0,9,0],
]


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


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    run_test("EASY", grid_easy)
    run_test("MEDIUM", grid_medium)
    run_test("HARD", grid_hard)