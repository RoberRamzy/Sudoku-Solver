import pygame
import board 
import sys

# --- CONFIGURATION ---
WIDTH = 630  
SIDEBAR = 200
SCREEN_WIDTH = WIDTH + SIDEBAR
CELL_SIZE = WIDTH // 9

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (50, 50, 200)
RED = (255, 0, 0)
LIGHT_BLUE = (230, 230, 255)

pygame.font.init()
FONT_LARGE = pygame.font.SysFont("Arial", 40, bold=True)
FONT_SMALL = pygame.font.SysFont("Arial", 16)
FONT_LABEL = pygame.font.SysFont("Arial", 18, bold=True)

# Button Rectangles
AI_BUTTON_RECT = pygame.Rect(WIDTH + 10, 200, 180, 50)
USER_BUTTON_RECT = pygame.Rect(WIDTH + 10, 270, 180, 50)
RANDOM_BUTTON_RECT = pygame.Rect(WIDTH + 10, 340, 180, 50)

ac3_generator = None
current_step = None
step_mode = False
recent_commit = None
show_all_steps = False

is_valid = True

def draw_grid(screen):
    screen.fill(WHITE)
    for i in range(10):
        thickness = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), thickness)
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thickness)

def draw_numbers(screen, sudoku_board, selected_cell):
    conflicts = sudoku_board.get_conflicts()
    for r in range(9):
        for c in range(9):
            val = sudoku_board.grid[r][c]
            if (r, c) == selected_cell:
                pygame.draw.rect(screen, LIGHT_BLUE, (c * CELL_SIZE + 2, r * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))
            
            if current_step and "xi" in current_step and "xj" in current_step:
                if (r, c) == current_step["xi"]:
                    pygame.draw.rect(screen, (100, 200, 255), (c * CELL_SIZE + 2, r * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))
                elif (r, c) == current_step["xj"]:
                    pygame.draw.rect(screen, (255, 150, 150), (c * CELL_SIZE + 2, r * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))
                
                if "xi" in current_step and "xj" in current_step:
                    xi = current_step["xi"]
                    xj = current_step["xj"]

                    x1 = xi[1] * CELL_SIZE + CELL_SIZE // 2
                    y1 = xi[0] * CELL_SIZE + CELL_SIZE // 2

                    x2 = xj[1] * CELL_SIZE + CELL_SIZE // 2
                    y2 = xj[0] * CELL_SIZE + CELL_SIZE // 2

                    if current_step.get("changed", False):
                        line_color = (0, 170, 0)   # GREEN = meaningful arc
                        width = 3
                    else:
                        line_color = (160, 160, 160)  # GRAY = useless arc
                        width = 1

                    pygame.draw.line(screen, line_color, (x1, y1), (x2, y2), width)

            if (r, c) == recent_commit:
                pygame.draw.rect(screen, (255, 255, 150), (c * CELL_SIZE + 2, r * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))
            
            if val != 0:
                color = BLACK if sudoku_board.initial_fixed[r][c] else BLUE
                if (r, c) in conflicts: color = RED
                text = FONT_LARGE.render(str(val), True, color)
                rect = text.get_rect(center=(c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, rect)
            else:
                draw_pencil_marks(screen, sudoku_board.domains[(r, c)], r, c)

def draw_pencil_marks(screen, domain, r, c):
    for val in domain:
        sub_r = (val - 1) // 3
        sub_c = (val - 1) % 3
        x = c * CELL_SIZE + (sub_c * (CELL_SIZE // 3)) + 8
        y = r * CELL_SIZE + (sub_r * (CELL_SIZE // 3)) + 4
        text = FONT_SMALL.render(str(val), True, GRAY)
        screen.blit(text, (x, y))

def draw_sidebar(screen, current_mode):
    pygame.draw.rect(screen, GRAY, (WIDTH, 0, SIDEBAR, WIDTH))
    
    # AI Mode Button
    ai_color = BLUE if current_mode == "AI" else BLACK
    pygame.draw.rect(screen, ai_color, AI_BUTTON_RECT, 2)
    ai_text = FONT_LABEL.render("MODE: AI SOLVE", True, ai_color)
    screen.blit(ai_text, (AI_BUTTON_RECT.x + 15, AI_BUTTON_RECT.y + 15))

    # User Mode Button
    user_color = BLUE if current_mode == "USER" else BLACK
    pygame.draw.rect(screen, user_color, USER_BUTTON_RECT, 2)
    user_text = FONT_LABEL.render("MODE: USER INPUT", True, user_color)
    screen.blit(user_text, (USER_BUTTON_RECT.x + 10, USER_BUTTON_RECT.y + 15))

    # Random Puzzle Button
    pygame.draw.rect(screen, (0, 140, 0), RANDOM_BUTTON_RECT, 2)
    rand_text = FONT_LABEL.render("RANDOM PUZZLE", True, (0, 140, 0))
    screen.blit(rand_text, (RANDOM_BUTTON_RECT.x + 10, RANDOM_BUTTON_RECT.y + 15))

    status_text = "VALID" if is_valid else "INVALID"
    color = (0, 150, 0) if is_valid else (200, 0, 0)
    label = FONT_LABEL.render(f"STATUS: {status_text}", True, color)
    screen.blit(label, (WIDTH + 10, 150))

    mode_text = "FULL ARC STEPS" if show_all_steps else "SKIP BORING STEPS"
    mode_color = (200, 0, 0) if show_all_steps else (0, 120, 0)
    label = FONT_SMALL.render(mode_text, True, mode_color)
    screen.blit(label, (WIDTH + 10, 400))

    # Small instruction footer
    instr = ["S: Solve board", "N: Next AC3 step", "M: Toggle step mode", "R: Reset board"]
    for i, txt in enumerate(instr):
        label = FONT_SMALL.render(txt, True, BLACK)
        screen.blit(label, (WIDTH + 15, 430 + i * 18))

def main():
    global ac3_generator, current_step, recent_commit, show_all_steps, is_valid
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, WIDTH))
    pygame.display.set_caption("Sudoku")
    
    sudoku_board = board.Board()
    # Sample starting numbers
    DEFAULT_PUZZLE = [
        [7, 9, 0, 0, 1, 3, 6, 0, 0],
        [4, 0, 0, 0, 7, 0, 3, 0, 0],
        [1, 0, 0, 2, 4, 0, 9, 7, 5],
        [5, 0, 0, 6, 0, 0, 2, 0, 7],
        [0, 7, 0, 0, 0, 1, 8, 0, 0],
        [8, 0, 6, 9, 2, 0, 5, 0, 0],
        [6, 0, 1, 0, 0, 2, 0, 5, 3],
        [3, 0, 0, 0, 0, 0, 4, 0, 9],
        [0, 2, 4, 0, 3, 5, 0, 0, 0]
    ]
    
    def load_puzzle(puzzle_grid):
        """Creates a fresh board loaded with the given 9x9 grid."""
        b = board.Board()
        for r in range(9):
            for c in range(9):
                if puzzle_grid[r][c] != 0:
                    b.set_cell(r, c, puzzle_grid[r][c], True)
        b.initial_reduction()
        return b

    sudoku_board = load_puzzle(DEFAULT_PUZZLE)

    selected_cell = None
    current_mode = "USER" # Initial Mode
    running = True
    generating    = False  # flag while random puzzle is being generated

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if AI_BUTTON_RECT.collidepoint(pos):
                    current_mode = "AI"
                    selected_cell = None # Deselect when switching to AI
                elif USER_BUTTON_RECT.collidepoint(pos):
                    current_mode = "USER"
                elif RANDOM_BUTTON_RECT.collidepoint(pos):
                    # Generate a fresh random solvable puzzle
                    ac3_generator = None
                    current_step  = None
                    recent_commit = None
                    is_valid      = True
                    selected_cell = None
                    sudoku_board  = board.Board()
                    sudoku_board.generate_random_puzzle(clues=30)

                elif pos[0] < WIDTH:
                    selected_cell = (pos[1] // CELL_SIZE, pos[0] // CELL_SIZE)

            if event.type == pygame.KEYDOWN:
                if current_mode == "USER" and selected_cell:
                    r, c = selected_cell
            
                    if not sudoku_board.initial_fixed[r][c]:
                        
                        # 1. Handle clearing the cell
                        if event.key in [pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0]:
                            sudoku_board.set_cell(r, c, 0)
                            sudoku_board.initial_reduction()
                            is_valid = True  # recalculate below

                        # 2. Handle ANY number input (Top row or Numpad)
                        elif event.unicode.isdigit():
                            val = int(event.unicode)
                            if 1 <= val <= 9: # We don't want 0 here since we handle it above
                                sudoku_board.set_cell(r, c, val)
                                sudoku_board.initial_reduction()
                                is_valid = (len(sudoku_board.get_conflicts()) == 0 and
                                            sudoku_board.is_solvable())

                if event.key == pygame.K_s:
                    sudoku_board.ac3()
                    sudoku_board.backtrack_solve()
                    ac3_generator = None
                    current_step  = None
                    recent_commit = None

                
                if event.key == pygame.K_m:
                    show_all_steps = not show_all_steps
                
                if event.key == pygame.K_n:
                    recent_commit = None

                    # Lazily create the generator the first time N is pressed
                    if ac3_generator is None:
                        ac3_generator = sudoku_board.ac3_steps()

                    # First: commit any singleton domain that is already resolved
                    committed = False
                    for (row, col), domain in sudoku_board.domains.items():
                        if sudoku_board.grid[row][col] == 0 and len(domain) == 1:
                            val = list(domain)[0]
                            sudoku_board.set_cell(row, col, val)
                            recent_commit = (row, col)
                            committed = True
                            break

                    if not committed:
                        try:
                            while True:
                                current_step = next(ac3_generator)

                                # AC3 finished — clean up and let backtracking finish
                                if current_step.get("done"):
                                    ac3_generator = None
                                    # If cells still remain, backtrack to fill them
                                    if sudoku_board.find_unassigned():
                                        sudoku_board.backtrack_solve()
                                    break

                                # AC3 found a contradiction — nothing more to do
                                if current_step.get("fail"):
                                    ac3_generator = None
                                    break

                                # In show-all mode: stop on every arc
                                if show_all_steps:
                                    break

                                # In skip mode: stop only when a domain actually shrank
                                if current_step.get("changed", False):
                                    break

                                # Boring step in skip mode: redraw and keep looping
                                draw_grid(screen)
                                draw_numbers(screen, sudoku_board, selected_cell)
                                draw_sidebar(screen, current_mode)
                                pygame.display.flip()
                                pygame.event.pump()  # keep OS responsive

                        except StopIteration:
                            ac3_generator = None
                            # Generator exhausted without a done/fail — finish with backtrack
                            if sudoku_board.find_unassigned():
                                sudoku_board.backtrack_solve()
                                
                if event.key == pygame.K_r:
                    sudoku_board  = load_puzzle(DEFAULT_PUZZLE)
                    ac3_generator = None   # FIX: clear stale generator
                    current_step  = None
                    recent_commit = None
                    is_valid      = True   # FIX: reset validity flag
                    selected_cell = None
                    current_mode  = "USER"


        draw_grid(screen)
        draw_numbers(screen, sudoku_board, selected_cell)
        draw_sidebar(screen, current_mode)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()