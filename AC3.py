# revise domain of xi given domain of xj
# returns true if the domain of xi was changed
def revise(board, xi, xj):
    revised = False
    # create a copy of the set to safely iterate while modifying the original
    for x in list(board.domains[xi]):
        if all(x == y for y in board.domains[xj]):
            board.domains[xi].remove(x)
            revised = True
            print(f"Tree update: Arc {xi} -> {xj}. Removed {x}. New domain: {board.domains[xi]}")
    return revised

# enforce arc consistency for all variable to solve or simplify the board
def ac3(board):
    print("AC-3 Algorithm Triggered")

    # initialize the queue with all arcs
    queue = []
    for r in range(9):
        for c in range(9):
            xi = (r, c)
            for xj in board.get_neighbors(r,c):
                queue.append((xi, xj))

    # apply arc consistency
    while queue:
        xi, xj = queue.pop(0)

        if revise(board, xi, xj):
            # if domain becomes empty, sudoku is unsolvable
            if len(board.domains[xi]) == 0:
                print("Unsolvable: Domain wiped out.")
                return False
            
            # if xi's domain was reduced, re-evaluate all it neighbors (except xj)
            for xk in board.get_neighbors(xi[0], xi[1]):
                if xk != xj:
                    queue.append((xk, xi))

    # update sudoku grid based on reduced domains
    changes_made = True
    while changes_made:
        changes_made = False
        for r in range(9):
            for c in range(9):
                # check for empty cells that now have a singelton domain
                if board.grid[r][c] == 0 and len(board.domains[(r, c)]) == 1:
                    val = list(board.domains[(r, c)])[0]
                    board.set_cell(r, c, val)
                    for neighbor in board.get_neighbors(r, c):
                        queue.append((neighbor, (r, c)))
                    changes_made = True

    print("AC-3 Algorithm Completed!")
    return True