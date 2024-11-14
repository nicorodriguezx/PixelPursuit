import pygame
import sys
import random

LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (220, 220, 220)
OVERLAY_BACKGROUND = (0, 0, 0, 128)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
TEXT_COLOR = (255, 255, 255)

class GameState:
    def __init__(self, width, height):
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.show_fps = False
        
        margin_percent = 0.05
        self.margin_x = int(width * margin_percent)
        self.margin_y = int(height * margin_percent)
        
        self.game_area_width = width - (2 * self.margin_x)
        self.game_area_height = height - (2 * self.margin_y)
        
        self.width = width
        self.height = height
        
        square_percent = 0.08
        self.square_size = int(self.game_area_height * square_percent)
        
        self.square_x1 = self.margin_x + (self.game_area_width // 4)
        self.square_y1 = self.margin_y + (self.game_area_height // 2)
        self.square_x2 = self.margin_x + ((self.game_area_width * 3) // 4)
        self.square_y2 = self.margin_y + (self.game_area_height // 2)
        
        self.speed = int(self.game_area_width * 0.00625)
        
        target_percent = 0.05
        self.target_size = int(self.game_area_height * target_percent)
        self.target_x = self.margin_x + random.randint(0, self.game_area_width - self.target_size)
        self.target_y = self.margin_y + random.randint(0, self.game_area_height - self.target_size)
        
        self.score1 = 0
        self.score2 = 0
        self.paused = False

    def set_fps(self, new_fps):
        self.FPS = max(1, min(new_fps, 144))
    
    def toggle_fps_display(self):
        self.show_fps = not self.show_fps
    
    def get_current_fps(self):
        return int(self.clock.get_fps())

pygame.init()

display_info = pygame.display.Info()
default_width = int(display_info.current_w * 0.8)
default_height = int(display_info.current_h * 0.8)
width = default_width
height = default_height

screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("PixelPursuit")
is_fullscreen = False

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def init_joysticks():
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()

    if joystick_count < 1:
        print("No joysticks found. Exiting...")
        pygame.quit()
        sys.exit()

    joysticks = [pygame.joystick.Joystick(i) for i in range(min(joystick_count, 2))]
    for joystick in joysticks:
        joystick.init()
        print(f"Initialized {joystick.get_name()} with {joystick.get_numbuttons()} buttons")
    return joysticks

def update_square_position(game_state, player_index, joystick):
    axis_x = joystick.get_axis(0)
    axis_y = joystick.get_axis(1)
    
    if player_index == 0:
        game_state.square_x1 += int(axis_x * game_state.speed)
        game_state.square_y1 += int(axis_y * game_state.speed)
        game_state.square_x1 = max(game_state.margin_x, 
                                 min(game_state.square_x1,
                                     game_state.margin_x + game_state.game_area_width - game_state.square_size))
        game_state.square_y1 = max(game_state.margin_y, 
                                 min(game_state.square_y1,
                                     game_state.margin_y + game_state.game_area_height - game_state.square_size))
    else:
        game_state.square_x2 += int(axis_x * game_state.speed)
        game_state.square_y2 += int(axis_y * game_state.speed)
        game_state.square_x2 = max(game_state.margin_x, 
                                 min(game_state.square_x2,
                                     game_state.margin_x + game_state.game_area_width - game_state.square_size))
        game_state.square_y2 = max(game_state.margin_y, 
                                 min(game_state.square_y2,
                                     game_state.margin_y + game_state.game_area_height - game_state.square_size))

def check_collision_and_update(game_state, player_index):
    if player_index == 0:
        square_x = game_state.square_x1
        square_y = game_state.square_y1
    else:
        square_x = game_state.square_x2
        square_y = game_state.square_y2

    if (square_x < game_state.target_x + game_state.target_size and
        square_x + game_state.square_size > game_state.target_x and
        square_y < game_state.target_y + game_state.target_size and
        square_y + game_state.square_size > game_state.target_y):
        
        if player_index == 0:
            game_state.score1 += 1
        else:
            game_state.score2 += 1
        
        spawn_new_target(game_state)
        return True
    return False

def spawn_new_target(game_state):
    game_state.target_x = game_state.margin_x + random.randint(0, game_state.game_area_width - game_state.target_size)
    game_state.target_y = game_state.margin_y + random.randint(0, game_state.game_area_height - game_state.target_size)

def draw_squares(game_state):
    pygame.draw.rect(screen, RED, (game_state.square_x1, game_state.square_y1, 
                                 game_state.square_size, game_state.square_size))
    pygame.draw.rect(screen, BLUE, (game_state.square_x2, game_state.square_y2, 
                                  game_state.square_size, game_state.square_size))

def draw_target(game_state):
    pygame.draw.rect(screen, GREEN, (game_state.target_x, game_state.target_y, 
                                   game_state.target_size, game_state.target_size))

def draw_scores(game_state):
    font_size = int(game_state.height * 0.06)
    font = pygame.font.Font(None, font_size)
    score_text = font.render(f"Player 1 Score: {game_state.score1}  Player 2 Score: {game_state.score2}", 
                           True, (0, 0, 0))
    margin = int(game_state.width * 0.0125)
    screen.blit(score_text, (margin, margin))

def draw_game_area(game_state):
    screen.fill(LIGHT_GRAY)
    pygame.draw.rect(screen, DARK_GRAY, 
                    (game_state.margin_x, game_state.margin_y,
                     game_state.game_area_width, game_state.game_area_height))

def draw_fps(game_state):
    if game_state.show_fps:
        font = pygame.font.Font(None, int(game_state.height * 0.03))
        fps_text = font.render(f"FPS: {game_state.get_current_fps()}", True, (0, 0, 0))
        screen.blit(fps_text, (game_state.width - fps_text.get_width() - 10, 10))

def toggle_fullscreen(game_state):
    global screen, width, height, is_fullscreen
    is_fullscreen = not is_fullscreen
    
    if is_fullscreen:
        width = display_info.current_w
        height = display_info.current_h
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    else:
        width = default_width
        height = default_height
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    
    game_state.width = width
    game_state.height = height
    game_state.margin_x = int(width * 0.05)
    game_state.margin_y = int(height * 0.05)
    game_state.game_area_width = width - (2 * game_state.margin_x)
    game_state.game_area_height = height - (2 * game_state.margin_y)
    
    game_state.square_size = int(game_state.game_area_height * 0.08)
    game_state.speed = int(game_state.game_area_width * 0.00625)
    game_state.target_size = int(game_state.game_area_height * 0.05)
    
    game_state.square_x1 = max(game_state.margin_x,
                              min(game_state.square_x1,
                                  game_state.margin_x + game_state.game_area_width - game_state.square_size))
    game_state.square_y1 = max(game_state.margin_y,
                              min(game_state.square_y1,
                                  game_state.margin_y + game_state.game_area_height - game_state.square_size))
    game_state.square_x2 = max(game_state.margin_x,
                              min(game_state.square_x2,
                                  game_state.margin_x + game_state.game_area_width - game_state.square_size))
    game_state.square_y2 = max(game_state.margin_y,
                              min(game_state.square_y2,
                                  game_state.margin_y + game_state.game_area_height - game_state.square_size))
    game_state.target_x = max(game_state.margin_x,
                             min(game_state.target_x,
                                 game_state.margin_x + game_state.game_area_width - game_state.target_size))
    game_state.target_y = max(game_state.margin_y,
                             min(game_state.target_y,
                                 game_state.margin_y + game_state.game_area_height - game_state.target_size))

def draw_options_screen(game_state):
    overlay = pygame.Surface((game_state.width, game_state.height), pygame.SRCALPHA)
    overlay.fill(OVERLAY_BACKGROUND)
    screen.blit(overlay, (0, 0))
    
    button_width = int(game_state.width * 0.3)
    button_height = int(game_state.height * 0.1)
    button_x = game_state.width // 2 - button_width // 2
    
    buttons = [
        {"text": "Resume", "y": 0.3},
        {"text": "Toggle Fullscreen", "y": 0.45},
        {"text": "Quit", "y": 0.6}
    ]
    
    mouse_pos = pygame.mouse.get_pos()
    
    font_large = pygame.font.Font(None, int(game_state.height * 0.08))
    title = font_large.render("Game Paused", True, TEXT_COLOR)
    title_rect = title.get_rect(center=(game_state.width // 2, game_state.height * 0.15))
    screen.blit(title, title_rect)
    
    font = pygame.font.Font(None, int(game_state.height * 0.04))
    for button in buttons:
        button_y = int(game_state.height * button["y"])
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, TEXT_COLOR, button_rect, 2)
        
        text = font.render(button["text"], True, TEXT_COLOR)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
        
        button["rect"] = button_rect

    return buttons

def handle_options_click(pos, buttons, game_state):
    for button in buttons:
        if button["rect"].collidepoint(pos):
            if button["text"] == "Resume":
                game_state.paused = False
            elif button["text"] == "Toggle Fullscreen":
                toggle_fullscreen(game_state)
            elif button["text"] == "Quit":
                pygame.quit()
                sys.exit()

def check_pause_input(event, joysticks, game_state):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        game_state.paused = not game_state.paused
        return True
    
    elif event.type == pygame.JOYBUTTONDOWN:
        if event.button in [7, 9]:
            game_state.paused = not game_state.paused
            return True
    return False

game_state = GameState(width, height)
joysticks = init_joysticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif check_pause_input(event, joysticks, game_state):
            pass
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen(game_state)
            elif event.key == pygame.K_F3:
                game_state.toggle_fps_display()
            elif event.key == pygame.K_F6:
                game_state.set_fps(game_state.FPS - 10)
            elif event.key == pygame.K_F7:
                game_state.set_fps(game_state.FPS + 10)
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state.paused:
            buttons = draw_options_screen(game_state)
            handle_options_click(event.pos, buttons, game_state)

    if not game_state.paused:
        for i, joystick in enumerate(joysticks):
            pygame.event.pump()
            update_square_position(game_state, i, joystick)
            check_collision_and_update(game_state, i)

    draw_game_area(game_state)
    draw_squares(game_state)
    draw_target(game_state)
    draw_scores(game_state)
    draw_fps(game_state)

    if game_state.paused:
        draw_options_screen(game_state)

    pygame.display.flip()

    game_state.clock.tick(game_state.FPS)

pygame.quit()

