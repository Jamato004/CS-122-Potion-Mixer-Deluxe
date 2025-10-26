import pygame
import os

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = "menu"  # Could later be "mixing", "results", etc.
        self.font = self.load_font()
        self.title_text = self.font.render("Potion Mixer Deluxe", True, (255, 255, 255))

    def load_font(self):
        font_path = os.path.join("assets", "fonts", "MedievalSharp-Regular.ttf")
        if not os.path.exists(font_path):
            # Fallback to system font if custom one is missing
            return pygame.font.SysFont(None, 48)
        return pygame.font.Font(font_path, 48)

    def handle_event(self, event):
        if self.state == "menu":
            # Press any key to start (temporary behavior)
            if event.type == pygame.KEYDOWN:
                self.state = "mixing"

    def update(self):
        # Update logic depending on current state
        pass

    def draw(self):
        self.screen.fill((25, 10, 40))  # Dark purple background
        if self.state == "menu":
            self.screen.blit(self.title_text, (200, 280))
            small_font = pygame.font.Font(None, 32)
            text = small_font.render("Press any key to start mixing...", True, (200, 200, 200))
            self.screen.blit(text, (260, 350))
        elif self.state == "mixing":
            # Placeholder screen for mixing stage
            font = pygame.font.Font(None, 48)
            text = font.render("Mixing Screen (WIP)", True, (255, 255, 255))
            self.screen.blit(text, (280, 300))
