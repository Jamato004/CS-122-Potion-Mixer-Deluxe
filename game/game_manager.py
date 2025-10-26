import pygame
import os
from game.ui import Button

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = "menu"
        self.font = self.load_font()
        self.small_font = pygame.font.Font(None, 32)
        self.load_music() # play music on startup

        # Temporary buttons
        self.start_button = Button("Start Mixing", 360, 340, 240, 60, self.small_font)
        self.back_button = Button("Back to Menu", 20, 20, 200, 50, self.small_font)

    def load_font(self):
        font_path = os.path.join("assets", "fonts", "MedievalSharp-Regular.ttf")
        if not os.path.exists(font_path):
            return pygame.font.SysFont(None, 48)
        return pygame.font.Font(font_path, 48)
    
    def load_music(self):
        music_path = os.path.join("assets", "sounds", "background.ogg")
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # -1 = loop forever
            pygame.mixer.music.set_volume(0.2)  # add volume slider later
        except Exception as e:
            print("Error loading background music:", e)


    def handle_event(self, event):
        # send to game
        if self.state == "menu":
            if self.start_button.is_clicked(event):
                self.state = "mixing"

        # send to main menu
        elif self.state == "mixing":
            if self.back_button.is_clicked(event):
                self.state = "menu"

    def update(self):
        # Add update logic here if needed later
        pass

    def draw(self):
        self.screen.fill((25, 10, 40))  # Dark purple background

        if self.state == "menu":
            title = self.font.render("Potion Mixer Deluxe", True, (255, 255, 255))
            self.screen.blit(title, (250, 200))
            self.start_button.draw(self.screen)

        elif self.state == "mixing":
            text = self.font.render("Mixing Screen (WIP)", True, (255, 255, 255))
            self.screen.blit(text, (260, 250))
            self.back_button.draw(self.screen)
