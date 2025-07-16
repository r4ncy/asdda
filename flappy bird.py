import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
GRAVITY = 0.25
JUMP_SPEED = -7
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds
FPS = 60

# Colors
WHITE = (255, 255, 255)
SKY_BLUE = (113, 197, 207)
PIPE_GREEN = (95, 168, 37)
GROUND_COLOR = (222, 216, 149)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

def create_bird_surface():
    surface = pygame.Surface((40, 30), pygame.SRCALPHA)
    # Body
    pygame.draw.ellipse(surface, (255, 255, 0), (0, 0, 30, 30))  # Yellow body
    # Eye
    pygame.draw.circle(surface, WHITE, (25, 10), 6)
    pygame.draw.circle(surface, (0, 0, 0), (25, 10), 3)
    # Beak
    pygame.draw.polygon(surface, (255, 165, 0), [(30, 15), (40, 10), (30, 20)])
    # Wing
    pygame.draw.ellipse(surface, (218, 218, 0), (5, 10, 15, 10))
    return surface

def create_pipe_surface():
    surface = pygame.Surface((50, WINDOW_HEIGHT), pygame.SRCALPHA)
    
    # Main pipe body
    pygame.draw.rect(surface, PIPE_GREEN, (0, 0, 50, WINDOW_HEIGHT))
    
    # Pipe cap
    cap_height = 30
    pygame.draw.rect(surface, (82, 147, 32), (0, 0, 50, cap_height))
    pygame.draw.rect(surface, (82, 147, 32), (-5, cap_height, 60, 10))
    
    # Highlight
    pygame.draw.rect(surface, (108, 183, 41), (5, 0, 10, WINDOW_HEIGHT))
    
    return surface

# Create game assets
bird_surface = create_bird_surface()
pipe_surface = create_pipe_surface()

class Bird:
    def __init__(self):
        self.x = WINDOW_WIDTH // 3
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x + 5, self.y + 5, 25, 25)
        self.angle = 0
        self.animation_time = 0
        self.wing_up = False

    def jump(self):
        self.velocity = JUMP_SPEED
        self.angle = 30

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y + 5
        
        # Update rotation based on velocity
        self.angle = max(-70, min(30, -self.velocity * 4))
        
        # Wing flap animation
        self.animation_time += 1
        if self.animation_time >= 15:
            self.animation_time = 0
            self.wing_up = not self.wing_up

    def draw(self):
        bird_copy = bird_surface.copy()
        if self.wing_up:
            # Animate wing
            pygame.draw.ellipse(bird_copy, (218, 218, 0), (5, 8, 15, 10))
        
        rotated_bird = pygame.transform.rotate(bird_copy, self.angle)
        screen.blit(rotated_bird, (self.x - rotated_bird.get_width()//2, 
                                 self.y - rotated_bird.get_height()//2))

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(200, WINDOW_HEIGHT - 200)
        self.x = WINDOW_WIDTH
        self.width = 50
        self.passed = False
        
        # Create rectangles for collision detection
        self.top_pipe = pygame.Rect(
            self.x,
            0,
            self.width,
            self.gap_y - PIPE_GAP // 2
        )
        self.bottom_pipe = pygame.Rect(
            self.x,
            self.gap_y + PIPE_GAP // 2,
            self.width,
            WINDOW_HEIGHT - (self.gap_y + PIPE_GAP // 2)
        )

    def update(self):
        self.x -= PIPE_SPEED
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x

    def draw(self):
        # Draw top pipe (flipped)
        top_pipe = pygame.transform.flip(pipe_surface, False, True)
        top_pipe = pygame.transform.scale(top_pipe, (self.width, self.top_pipe.height))
        screen.blit(top_pipe, self.top_pipe)
        
        # Draw bottom pipe
        bottom_pipe = pygame.transform.scale(pipe_surface, (self.width, self.bottom_pipe.height))
        screen.blit(bottom_pipe, self.bottom_pipe)

def draw_ground():
    ground_rect = pygame.Rect(0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, 50)
    pygame.draw.rect(screen, GROUND_COLOR, ground_rect)
    # Add stripes
    for i in range(0, WINDOW_WIDTH, 30):
        pygame.draw.line(screen, (209, 203, 139), 
                        (i, WINDOW_HEIGHT - 50), 
                        (i + 15, WINDOW_HEIGHT), 
                        3)

def main():
    bird = Bird()
    pipes = []
    score = 0
    high_score = 0
    last_pipe = pygame.time.get_ticks()
    font = pygame.font.Font(None, 48)
    game_active = False
    
    # Game loop
    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        bird.jump()
                    else:
                        bird = Bird()
                        pipes = []
                        score = 0
                        last_pipe = current_time
                        game_active = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_active:
                    bird.jump()
                else:
                    bird = Bird()
                    pipes = []
                    score = 0
                    last_pipe = current_time
                    game_active = True

        # Draw background
        screen.fill(SKY_BLUE)
        
        if game_active:
            # Update bird
            bird.update()

            # Create new pipes
            if current_time - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe = current_time

            # Update and check pipes
            for pipe in pipes[:]:
                pipe.update()
                
                # Remove off-screen pipes
                if pipe.x + pipe.width < 0:
                    pipes.remove(pipe)
                
                # Check for collisions
                if (bird.rect.colliderect(pipe.top_pipe) or 
                    bird.rect.colliderect(pipe.bottom_pipe)):
                    game_active = False
                    if score > high_score:
                        high_score = score

                # Score points
                if not pipe.passed and pipe.x < bird.x:
                    score += 1
                    pipe.passed = True

            # Check if bird hits the ground or ceiling
            if bird.y < 0 or bird.y + bird.rect.height > WINDOW_HEIGHT - 50:
                game_active = False
                if score > high_score:
                    high_score = score

        # Draw game elements
        for pipe in pipes:
            pipe.draw()
            
        draw_ground()
        bird.draw()
        
        # Draw score
        score_text = font.render(f'{score}', True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 50))
        
        if not game_active:
            # Draw game over screen
            game_over_text = font.render('Game Over!', True, WHITE)
            screen.blit(game_over_text, 
                       (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2,
                        WINDOW_HEIGHT // 3))
            
            score_text = font.render(f'Score: {score}', True, WHITE)
            screen.blit(score_text,
                       (WINDOW_WIDTH // 2 - score_text.get_width() // 2,
                        WINDOW_HEIGHT // 2))
            
            high_score_text = font.render(f'Best: {high_score}', True, WHITE)
            screen.blit(high_score_text,
                       (WINDOW_WIDTH // 2 - high_score_text.get_width() // 2,
                        WINDOW_HEIGHT // 2 + 50))
            
            prompt_text = font.render('Click to play!', True, WHITE)
            screen.blit(prompt_text,
                       (WINDOW_WIDTH // 2 - prompt_text.get_width() // 2,
                        WINDOW_HEIGHT * 2 // 3))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()