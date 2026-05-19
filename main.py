import pygame

from game import Game, SelectCaseMode, GameStatus

# pygame setup
pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# grid configuration
GRID_COLS = 30
GRID_ROWS = 16
CELL_SIZE = 32
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_Y = 100

# top panel configuration
PANEL_HEIGHT = 80
PANEL_Y = GRID_Y - PANEL_HEIGHT - 10
PANEL_PADDING = 8
LEFT_RECT_WIDTH = 120
RIGHT_RECT_WIDTH = 120
CENTER_RECT_WIDTH = 960 - LEFT_RECT_WIDTH - RIGHT_RECT_WIDTH - PANEL_PADDING * 4

RESTART_BUTTON_WIDTH = 240
RESTART_BUTTON_HEIGHT = 60
RESTART_BUTTON_Y_OFFSET = 120

# colors
BG_COLOR = pygame.Color("#444c54")
GRID_COLOR = pygame.Color("#d9d9d9")
CELL_COLOR = pygame.Color("#5b6470")
PANEL_COLOR = pygame.Color("#2f363f")
BADGE_COLOR = pygame.Color("#bf1f1f")
TEXT_COLOR = pygame.Color("#ffffff")
LINE_COLOR = pygame.Color("#2c2f33")
BUTTON_COLOR = pygame.Color("#5a92d4")
BUTTON_HOVER_COLOR = pygame.Color("#7aa9e3")

font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 36)
# emoji-capable fonts
try:
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 48)
    icon_font = pygame.font.SysFont("Segoe UI Emoji", 28)
except Exception:
    emoji_font = pygame.font.SysFont(None, 48)
    icon_font = pygame.font.SysFont(None, 28)

DIFFICULTIES = {
    "Beginner": (8, 8, 10),
    "Intermediate": (16, 16, 40),
    "Expert": (30, 16, 99),
}

current_difficulty = None


def make_game(difficulty_name: str) -> Game:
    width, height, mines = DIFFICULTIES[difficulty_name]
    return Game(width=width, height=height, mines=mines)


current_select_mode = SelectCaseMode.DISCOVER
current_state = "menu"  # "menu" or "play"

game = None
game_over = False
final_status = None
running = True
while running:
    difficulty_names = list(DIFFICULTIES.keys())
    difficulty_button_width = 180
    difficulty_button_height = 40
    difficulty_spacing = 12
    total_difficulty_width = len(difficulty_names) * difficulty_button_width + (len(difficulty_names) - 1) * difficulty_spacing
    difficulty_x = (SCREEN_WIDTH - total_difficulty_width) // 2
    difficulty_y = 220
    difficulty_rects = []
    for index, name in enumerate(difficulty_names):
        rect = pygame.Rect(
            difficulty_x + index * (difficulty_button_width + difficulty_spacing),
            difficulty_y,
            difficulty_button_width,
            difficulty_button_height,
        )
        difficulty_rects.append((name, rect))

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and current_state == "menu":
                for difficulty_name, rect in difficulty_rects:
                    if rect.collidepoint(event.pos):
                        current_difficulty = difficulty_name
                        game = make_game(current_difficulty)
                        current_state = "play"
                        current_select_mode = SelectCaseMode.DISCOVER
                        game_over = False
                        final_status = None
                        break
                continue

            if current_state == "play":
                if game_over:
                    if event.button == 1:
                        restart_rect = pygame.Rect(
                            (SCREEN_WIDTH - RESTART_BUTTON_WIDTH) // 2,
                            SCREEN_HEIGHT // 2 + RESTART_BUTTON_Y_OFFSET,
                            RESTART_BUTTON_WIDTH,
                            RESTART_BUTTON_HEIGHT,
                        )
                        if restart_rect.collidepoint(event.pos):
                            current_state = "menu"
                            current_difficulty = None
                            game = None
                            current_select_mode = SelectCaseMode.DISCOVER
                            game_over = False
                            final_status = None
                    continue
                if event.button == 1:
                    # left click: toggle select mode when clicking the center button
                    if center_rect.collidepoint(event.pos):
                        if current_select_mode == SelectCaseMode.DISCOVER:
                            current_select_mode = SelectCaseMode.FLAG
                        else:
                            current_select_mode = SelectCaseMode.DISCOVER
                        continue
                if event.button in (1, 3):
                    # check if click is inside the grid area
                    mx, my = event.pos
                    if GRID_X <= mx < GRID_X + GRID_WIDTH and GRID_Y <= my < GRID_Y + GRID_HEIGHT:
                        col = (mx - GRID_X) // CELL_SIZE
                        row = (my - GRID_Y) // CELL_SIZE
                        # bounds safety
                        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                            try:
                                mode = SelectCaseMode.FLAG if event.button == 3 else current_select_mode
                                game.select_case((col, row), mode)
                            except Exception as e:
                                print(f"select_case error: {e}")


    if current_state == "play":
        GRID_COLS = game.grid.grid_width
        GRID_ROWS = game.grid.grid_height
        GRID_WIDTH = GRID_COLS * CELL_SIZE
        GRID_HEIGHT = GRID_ROWS * CELL_SIZE
        GRID_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
        GRID_Y = 100
        PANEL_Y = GRID_Y - PANEL_HEIGHT - 10

    # precompute top-panel rects so events can test collisions
    center_rect_width = 960 - LEFT_RECT_WIDTH - RIGHT_RECT_WIDTH - PANEL_PADDING * 4
        
    left_rect = pygame.Rect((SCREEN_WIDTH - 960) // 2 + PANEL_PADDING, PANEL_Y + PANEL_PADDING, LEFT_RECT_WIDTH, PANEL_HEIGHT - PANEL_PADDING * 2)
    center_rect = pygame.Rect(left_rect.right + PANEL_PADDING, PANEL_Y + PANEL_PADDING, center_rect_width, PANEL_HEIGHT - PANEL_PADDING * 2)
    right_rect = pygame.Rect((SCREEN_WIDTH - 960) // 2 + 960 - RIGHT_RECT_WIDTH - PANEL_PADDING, PANEL_Y + PANEL_PADDING, RIGHT_RECT_WIDTH, PANEL_HEIGHT - PANEL_PADDING * 2)

    # check game status regularly
    if current_state == "play":
        status = game.check_game_status()
        if status != GameStatus.ON_GOING and not game_over:
            final_status = status
            game_over = True

    screen.fill(BG_COLOR)

    if current_state == "menu":
        title_font = pygame.font.SysFont(None, 72)
        title_text = title_font.render("Minesweeper", True, TEXT_COLOR)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        info_text = small_font.render("Select a difficulty to start", True, TEXT_COLOR)
        screen.blit(info_text, info_text.get_rect(center=(SCREEN_WIDTH // 2, 180)))

        for difficulty_name, rect in difficulty_rects:
            button_color = BUTTON_COLOR if difficulty_name == current_difficulty else PANEL_COLOR
            pygame.draw.rect(screen, button_color, rect, border_radius=8)
            difficulty_text = small_font.render(difficulty_name, True, TEXT_COLOR)
            screen.blit(difficulty_text, difficulty_text.get_rect(center=rect.center))
    else:
        # draw top panel background
        pygame.draw.rect(screen, PANEL_COLOR, 
                         ((SCREEN_WIDTH - 960) // 2, PANEL_Y, 960, PANEL_HEIGHT),
                         border_radius=10)

        # draw left badge with supposed number of bomb left
        pygame.draw.rect(screen, BADGE_COLOR, left_rect, border_radius=8)
        left_text = font.render(f"{game.supposed_mines_left()}", True, TEXT_COLOR)
        screen.blit(left_text, left_text.get_rect(center=left_rect.center))

        # draw center button area (shows emoji based on current_select_mode)
        pygame.draw.rect(screen, CELL_COLOR, center_rect, border_radius=8)
        emoji = "🚩" if current_select_mode == SelectCaseMode.FLAG else "🔎"
        emoji_text = emoji_font.render(emoji, True, TEXT_COLOR)
        screen.blit(emoji_text, emoji_text.get_rect(center=center_rect.center))

        # draw right badge with number of flags used
        pygame.draw.rect(screen, BADGE_COLOR, right_rect, border_radius=8)
        right_text = font.render(f"{game.flags_placed()}", True, TEXT_COLOR)
        screen.blit(right_text, right_text.get_rect(center=right_rect.center))

        # draw grid cells with case state rendering
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                cell_x = GRID_X + col * CELL_SIZE
                cell_y = GRID_Y + row * CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                case = game.grid.cases[row][col]

                # show flag even on covered cells (highest priority)
                if case.is_flagged:
                    pygame.draw.rect(screen, CELL_COLOR, cell_rect)
                    flag_surf = icon_font.render("🚩", True, TEXT_COLOR)
                    screen.blit(flag_surf, flag_surf.get_rect(center=cell_rect.center))
                elif case.is_discovered:
                    # discovered cell background
                    discovered_bg = pygame.Color(220, 220, 220)
                    pygame.draw.rect(screen, discovered_bg, cell_rect)

                    # priority for discovered: bomb -> number (>0) -> empty (0)
                    if case.is_mine:
                        bomb_surf = icon_font.render("💣", True, TEXT_COLOR)
                        screen.blit(bomb_surf, bomb_surf.get_rect(center=cell_rect.center))
                    elif case.number_of_close_mines > 0:
                        num_surf = small_font.render(str(case.number_of_close_mines), True, LINE_COLOR)
                        screen.blit(num_surf, num_surf.get_rect(center=cell_rect.center))
                    else:
                        # discovered and zero adjacent mines: leave empty
                        pass
                else:
                    # covered cell
                    pygame.draw.rect(screen, CELL_COLOR, cell_rect)

                # cell border
                pygame.draw.rect(screen, LINE_COLOR, cell_rect, 1)

    if game_over and final_status is not None:
        result_text = "YOU WON!" if final_status == GameStatus.WON else "YOU LOST"
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        large_font = pygame.font.SysFont(None, 96)
        txt = large_font.render(result_text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        restart_rect = pygame.Rect(
            (SCREEN_WIDTH - RESTART_BUTTON_WIDTH) // 2,
            SCREEN_HEIGHT // 2 + RESTART_BUTTON_Y_OFFSET,
            RESTART_BUTTON_WIDTH,
            RESTART_BUTTON_HEIGHT,
        )
        pygame.draw.rect(screen, BUTTON_COLOR, restart_rect, border_radius=10)
        restart_text = small_font.render("Choose Difficulty", True, TEXT_COLOR)
        screen.blit(restart_text, restart_text.get_rect(center=restart_rect.center))

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
