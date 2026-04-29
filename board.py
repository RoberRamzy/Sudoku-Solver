import AC3

class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        
        self.initial_fixed = [[False for _ in range(9)] for _ in range(9)]
        # CSP Domains
        self.domains = {(r, c): set(range(1, 10)) for r in range(9) for c in range(9)}

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

    def ac3(self):
       return AC3.ac3(self)
    
    def find_unassigned(self):
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    return (r, c)
        return None

    def is_valid(self, r, c, val):
        for nr, nc in self.get_neighbors(r, c):
            if self.grid[nr][nc] == val:
                return False
        return True

    def backtrack_solve(self):
        cell = self.find_unassigned()
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

    def display(self):
        """Console print for debugging."""
        for row in self.grid:
            print(' '.join(str(cell) if cell != 0 else "." for cell in row))