import AC3

import time

class Metrics:
    def __init__(self):
        self.arc_checks = 0
        self.domain_reductions = 0
        self.queue_pushes = 0
        self.queue_pops = 0
        self.bt_calls = 0
        self.ac3_time = 0
        self.bt_time = 0

class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        
        self.initial_fixed = [[False for _ in range(9)] for _ in range(9)]
        # CSP Domains
        self.domains = {(r, c): set(range(1, 10)) for r in range(9) for c in range(9)}
        self.metrics = Metrics()
    
    def get_neighbors(self, row, col):
        
        neighbors = set()
        for i in range(9):
            neighbors.add((row, i)) # Row
            neighbors.add((i, col)) # Col
        
        # 3x3 Box logic
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                neighbors.add((r, c))
        
        neighbors.remove((row, col)) # Remove the cell itself
        return neighbors

    def set_cell(self, row, col, value, is_initial=False):
        """Sets a cell value and updates its fixed status and domain."""
        self.grid[row][col] = value
        if is_initial:
            self.initial_fixed[row][col] = True
        
        if value != 0:
            self.domains[(row, col)] = {value}
        else:
            self.domains[(row, col)] = set(range(1, 10))

    def initial_reduction(self):
        """removes fixed values from neighbor domains."""
        # Reset domains to full before recalculating
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    self.domains[(r, c)] = set(range(1, 10))
                else:
                    self.domains[(r, c)] = {self.grid[r][c]}

        # Prune based on current grid values
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] != 0:
                    val = self.grid[r][c]
                    for nr, nc in self.get_neighbors(r, c):
                        if val in self.domains[(nr, nc)]:
                            self.domains[(nr, nc)].remove(val)

    def get_conflicts(self):
        
        conflicts = set()
        for r in range(9):
            for c in range(9):
                val = self.grid[r][c]
                if val != 0:
                    for nr, nc in self.get_neighbors(r, c):
                        if self.grid[nr][nc] == val:
                            conflicts.add((r, c))
                            conflicts.add((nr, nc))
        return conflicts

    def ac3_steps(self):
       return AC3.ac3_steps(self)

    def ac3(self):
       return AC3.ac3(self)
    
    def find_unassigned(self):
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    return (r, c)
        return None
    def find_unassigned_mrv(self):
        best_cell = None
        best_domain_size = 10  # max is 9

        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    size = len(self.domains[(r, c)])

                    if size < best_domain_size:
                        best_domain_size = size
                        best_cell = (r, c)

                    # early exit: can't get better than 1
                    if best_domain_size == 1:
                        return best_cell

        return best_cell

    def is_valid(self, r, c, val):
        for nr, nc in self.get_neighbors(r, c):
            if self.grid[nr][nc] == val:
                return False
        return True

    def backtrack_solve(self):
        cell = self.find_unassigned_mrv()
        if not cell:
            return True

        r, c = cell

        for val in self.domains[(r, c)]:
            if self.is_valid(r, c, val):
                self.grid[r][c] = val

                if self.backtrack_solve():
                    return True

                self.grid[r][c] = 0

        return False
    
    def is_solvable(self):
        import copy
        temp = copy.deepcopy(self)
        return temp.backtrack_solve()

    def generate_random_puzzle(self, clues=30):
        """
        Generates a random solvable Sudoku puzzle using backtracking.
        1. Fill the board completely with a valid solution using randomized backtracking.
        2. Remove (81 - clues) cells, keeping the puzzle solvable.
        """
        import random, copy
        # Step 1: Reset board to empty
        self.grid = [[0]*9 for _ in range(9)]
        self.domains = {(r, c): set(range(1, 10)) for r in range(9) for c in range(9)}
        self.initial_fixed = [[False]*9 for _ in range(9)]
        # Step 2: Fill board with a full valid solution (randomized backtracking)
        def fill():
            cell = self.find_unassigned_mrv()
            if not cell:
                return True
            r, c = cell
            values = list(range(1, 10))
            random.shuffle(values)  # randomize order so each puzzle is unique
            for val in values:
                if self.is_valid(r, c, val):
                    self.grid[r][c] = val
                    if fill():
                        return True
                    self.grid[r][c] = 0
            return False
        fill()
        # Step 3: Remove cells one-by-one, checking solvability after each removal
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        removed = 0
        target_removals = 81 - clues
        for r, c in cells:
            if removed >= target_removals:
                break
            backup = self.grid[r][c]
            self.grid[r][c] = 0
            # Verify the puzzle is still uniquely solvable
            if self.is_solvable():
                removed += 1
            else:
                self.grid[r][c] = backup  # restore if removing breaks solvability
        # Step 4: Mark remaining filled cells as fixed/initial
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] != 0:
                    self.initial_fixed[r][c] = True
                    self.domains[(r, c)] = {self.grid[r][c]}
        self.initial_reduction()

    # BACK TRACKING WITH FORWARD CHECKING
    def forward_check(self, r, c, val):
        """
        Removes `val` from neighbors' domains.
        Returns False if any domain becomes empty.
        """

        for nb in self.get_neighbors(r, c):
            if val in self.domains[nb]:
                self.domains[nb].remove(val)

                if len(self.domains[nb]) == 0:
                    return False

        return True

    def copy_domains(self):
        return {k: v.copy() for k, v in self.domains.items()}
    
    def restore_domains(self, backup):
        self.domains = backup

    def backtrack_fc(self, metrics=None):
        if metrics:
            metrics.bt_calls += 1

        cell = self.find_unassigned_mrv()
        if not cell:
            return True

        r, c = cell

        for val in list(self.domains[(r, c)]):
            if self.is_valid(r, c, val):

                # backup state
                backup = self.copy_domains()
                old_val = self.grid[r][c]

                # assign
                self.grid[r][c] = val
                self.domains[(r, c)] = {val}

                # forward check
                ok = self.forward_check(r, c, val)

                if metrics and ok:
                    # domain reductions = how many values got removed
                    # (approximation-based but acceptable for reports)
                    metrics.domain_reductions += sum(
                        1 for nb in self.get_neighbors(r, c)
                        if val not in self.domains[nb]
                    )

                if ok and self.backtrack_fc(metrics):
                    return True

                # restore
                self.grid[r][c] = old_val
                self.restore_domains(backup)

        return False

    def display(self):
        """Console print for debugging."""
        for row in self.grid:
            print(' '.join(str(cell) if cell != 0 else "." for cell in row))