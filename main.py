import pygame
from game.game_manager import GameManager

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

# Create the main game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Potion Mixer Deluxe")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Create GameManager instance
game = GameManager(screen)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_event(event)

    # Update game logic
    game.update()

    # Draw everything
    game.draw()

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
