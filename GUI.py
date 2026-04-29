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

    # Small instruction footer
    instr = ["Press S to Solve", "Press R to Reset"]
    for i, txt in enumerate(instr):
        label = FONT_SMALL.render(txt, True, BLACK)
        screen.blit(label, (WIDTH + 15, 350 + i*20))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, WIDTH))
    pygame.display.set_caption("Sudoku")
    
    sudoku_board = board.Board()
    # Sample starting numbers
    puzzle = [
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
    for r in range(9):
        for c in range(9):
            if puzzle[r][c] != 0:
                sudoku_board.set_cell(r, c, puzzle[r][c], True)
    sudoku_board.initial_reduction()

    selected_cell = None
    current_mode = "USER" # Initial Mode
    running = True

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
                elif pos[0] < WIDTH:
                    selected_cell = (pos[1] // CELL_SIZE, pos[0] // CELL_SIZE)

            if event.type == pygame.KEYDOWN:
                if current_mode == "USER" and selected_cell:
                    r, c = selected_cell
                    if event.type == pygame.KEYDOWN:
               
                        if not sudoku_board.initial_fixed[r][c]:

                            # 1. Handle clearing the cell
                            if event.key in [pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0]:
                                sudoku_board.set_cell(r, c, 0)
                                sudoku_board.initial_reduction()

                            # 2. Handle ANY number input (Top row or Numpad)
                            elif event.unicode.isdigit():
                                val = int(event.unicode)
                                if 1 <= val <= 9: # We don't want 0 here since we handle it above
                                    sudoku_board.set_cell(r, c, val)
                                    sudoku_board.initial_reduction()

                            # --- Check DELETE/CLEAR ---
                            elif event.key in [pygame.K_0, pygame.K_KP0, pygame.K_BACKSPACE, pygame.K_DELETE]:
                                sudoku_board.set_cell(r, c, 0)
                                sudoku_board.initial_reduction()

                if event.key == pygame.K_s:
                    sudoku_board.ac3() 
                    
                
                if event.key == pygame.K_r:
                    sudoku_board = board.Board()
                    
                    selected_cell = None
                    current_mode = "USER"

        draw_grid(screen)
        draw_numbers(screen, sudoku_board, selected_cell)
        draw_sidebar(screen, current_mode)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()