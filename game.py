import pygame
import sys
import random

# After the color definitions, add new colors
LIGHT_GRAY = (240, 240, 240)  # Color for the margins
DARK_GRAY = (220, 220, 220)   # Color for the game area

class GameState:
    def __init__(self, width, height):
        # Frame rate settings
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.show_fps = False  # Option to display FPS
        
        # Calculate margins as percentage of screen dimensions
        margin_percent = 0.05  # 5% of screen dimensions
        self.margin_x = int(width * margin_percent)
        self.margin_y = int(height * margin_percent)
        
        # Game area dimensions
        self.game_area_width = width - (2 * self.margin_x)
        self.game_area_height = height - (2 * self.margin_y)
        
        # Rest of the properties scaled to game area instead of full screen
        self.width = width
        self.height = height
        
        # Square size as percentage of game area height
        square_percent = 0.08
        self.square_size = int(self.game_area_height * square_percent)
        
        # Initial positions within game area
        self.square_x1 = self.margin_x + (self.game_area_width // 4)
        self.square_y1 = self.margin_y + (self.game_area_height // 2)
        self.square_x2 = self.margin_x + ((self.game_area_width * 3) // 4)
        self.square_y2 = self.margin_y + (self.game_area_height // 2)
        
        # Speed relative to game area width
        self.speed = int(self.game_area_width * 0.00625)
        
        # Target size as percentage of game area height
        target_percent = 0.05
        self.target_size = int(self.game_area_height * target_percent)
        self.target_x = self.margin_x + random.randint(0, self.game_area_width - self.target_size)
        self.target_y = self.margin_y + random.randint(0, self.game_area_height - self.target_size)
        
        self.score1 = 0
        self.score2 = 0

    def set_fps(self, new_fps):
        """Change the target frame rate"""
        self.FPS = max(1, min(new_fps, 144))  # Clamp between 1 and 144 FPS
    
    def toggle_fps_display(self):
        """Toggle FPS counter display"""
        self.show_fps = not self.show_fps
    
    def get_current_fps(self):
        """Get the actual FPS (for display purposes)"""
        return int(self.clock.get_fps())

# Initialize Pygame
pygame.init()

# Get the display info
display_info = pygame.display.Info()
# Set default window size to 80% of screen size for windowed mode
default_width = int(display_info.current_w * 0.8)
default_height = int(display_info.current_h * 0.8)
width = default_width
height = default_height

# Initialize in windowed mode
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("PixelPursuit")
is_fullscreen = False

# Define colors
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
    return joysticks

def update_square_position(game_state, player_index, joystick):
    """Update square position directly in game state"""
    axis_x = joystick.get_axis(0)
    axis_y = joystick.get_axis(1)
    
    if player_index == 0:
        game_state.square_x1 += int(axis_x * game_state.speed)
        game_state.square_y1 += int(axis_y * game_state.speed)
        # Constrain movement to game area
        game_state.square_x1 = max(game_state.margin_x, 
                                 min(game_state.square_x1,
                                     game_state.margin_x + game_state.game_area_width - game_state.square_size))
        game_state.square_y1 = max(game_state.margin_y, 
                                 min(game_state.square_y1,
                                     game_state.margin_y + game_state.game_area_height - game_state.square_size))
    else:
        game_state.square_x2 += int(axis_x * game_state.speed)
        game_state.square_y2 += int(axis_y * game_state.speed)
        # Constrain movement to game area
        game_state.square_x2 = max(game_state.margin_x, 
                                 min(game_state.square_x2,
                                     game_state.margin_x + game_state.game_area_width - game_state.square_size))
        game_state.square_y2 = max(game_state.margin_y, 
                                 min(game_state.square_y2,
                                     game_state.margin_y + game_state.game_area_height - game_state.square_size))

def check_collision_and_update(game_state, player_index):
    """Check collision and update score/target if needed"""
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
        
        # Update score
        if player_index == 0:
            game_state.score1 += 1
        else:
            game_state.score2 += 1
        
        # Spawn new target
        spawn_new_target(game_state)
        return True
    return False

def spawn_new_target(game_state):
    """Update target position directly in game state"""
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
    # Scale font size based on screen height
    font_size = int(game_state.height * 0.06)  # 6% of screen height
    font = pygame.font.Font(None, font_size)
    score_text = font.render(f"Player 1 Score: {game_state.score1}  Player 2 Score: {game_state.score2}", 
                           True, (0, 0, 0))
    # Position score relative to screen size
    margin = int(game_state.width * 0.0125)  # 1.25% of screen width
    screen.blit(score_text, (margin, margin))

def draw_game_area(game_state):
    # Draw margin area
    screen.fill(LIGHT_GRAY)
    # Draw game area
    pygame.draw.rect(screen, DARK_GRAY, 
                    (game_state.margin_x, game_state.margin_y,
                     game_state.game_area_width, game_state.game_area_height))

def draw_fps(game_state):
    """Draw the current FPS if enabled"""
    if game_state.show_fps:
        font = pygame.font.Font(None, int(game_state.height * 0.03))
        fps_text = font.render(f"FPS: {game_state.get_current_fps()}", True, (0, 0, 0))
        screen.blit(fps_text, (game_state.width - fps_text.get_width() - 10, 10))

# Add this new function
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
    
    # Update game_state with new dimensions
    game_state.width = width
    game_state.height = height
    game_state.margin_x = int(width * 0.05)
    game_state.margin_y = int(height * 0.05)
    game_state.game_area_width = width - (2 * game_state.margin_x)
    game_state.game_area_height = height - (2 * game_state.margin_y)
    
    # Recalculate sizes based on new game area dimensions
    game_state.square_size = int(game_state.game_area_height * 0.08)
    game_state.speed = int(game_state.game_area_width * 0.00625)
    game_state.target_size = int(game_state.game_area_height * 0.05)
    
    # Adjust positions to keep them in bounds
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

# Initialize game state and joysticks
game_state = GameState(width, height)
joysticks = init_joysticks()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen(game_state)
            elif event.key == pygame.K_F3:  # Add FPS display toggle
                game_state.toggle_fps_display()
            # Optional: FPS adjustment keys
            elif event.key == pygame.K_F6:  # Decrease FPS
                game_state.set_fps(game_state.FPS - 10)
            elif event.key == pygame.K_F7:  # Increase FPS
                game_state.set_fps(game_state.FPS + 10)

    # Read joystick input for both joysticks
    for i, joystick in enumerate(joysticks):
        pygame.event.pump()
        update_square_position(game_state, i, joystick)
        check_collision_and_update(game_state, i)

    # Draw game elements
    draw_game_area(game_state)
    draw_squares(game_state)
    draw_target(game_state)
    draw_scores(game_state)
    draw_fps(game_state)

    # Update the display
    pygame.display.flip()

    # Frame rate control using GameState clock
    game_state.clock.tick(game_state.FPS)

# Clean up
pygame.quit()

