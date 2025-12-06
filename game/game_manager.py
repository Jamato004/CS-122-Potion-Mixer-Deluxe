import pygame
from game.ui import Button
from game.assets_loader import load_font, load_music
from game.mixing_scene import MixingScene
from game.level_select_scene import LevelSelectScene


class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = "menu"

        # Fonts
        self.font = load_font(size=48)
        self.small_font = pygame.font.Font(None, 28)

        # Menu buttons
        self.start_button = Button("Start Mixing", 360, 340, 240, 60, self.small_font)
        self.back_button = Button("Back to Menu", 20, 20, 200, 50, self.small_font)

        # Scenes
        self.mixing_scene = MixingScene(screen, self.small_font)
        self.level_select_scene = LevelSelectScene(screen, self.small_font)
        self.mixing_scene.on_level_complete = self._handle_level_complete



        # Load music
        load_music("background.ogg")

    # Level Helper
    def start_level(self, level_number):
        self.mixing_scene.load_level(level_number)
        self.mixing_scene.retry_count = 0  # reset retries
        self.state = "mixing"

        

    def _handle_level_complete(self, level, retries):
        self.level_select_scene.update_best_retry(level, retries)
        self.level_select_scene.refresh()

    # ---------------- Event Handling ----------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return

        if self.state == "menu":
            if self.start_button.is_clicked(event):
                self.state = "level_select"
            return

        elif self.state == "level_select":
            self.level_select_scene.handle_event(event, self)
            return

        elif self.state == "mixing":
            self.mixing_scene.handle_event(event)
            if self.back_button.is_clicked(event):
                self.state = "level_select"
            return




    # ---------------- Update ----------------
    def update(self):
        if self.state == "mixing":
            self.mixing_scene.update()

    # ---------------- Draw ----------------
    def draw(self):
        self.screen.fill((30, 10, 40))

        if self.state == "menu":
            title = self.font.render("Potion Mixer Deluxe", True, (255, 255, 255))
            self.screen.blit(title, (250, 200))
            self.start_button.draw(self.screen)

        elif self.state == "level_select":
            self.level_select_scene.draw()

        elif self.state == "mixing":
            self.mixing_scene.draw()
            self.back_button.draw(self.screen)
