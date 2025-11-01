import pygame
import os
from game.ui import Button, draw_slot
from game.assets_loader import *

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = "menu"
        self.font = self.load_font()
        self.small_font = pygame.font.Font(None, 28)

        # Temporary buttons
        self.start_button = Button("Start Mixing", 360, 340, 240, 60, self.small_font)
        self.back_button = Button("Back to Menu", 20, 20, 200, 50, self.small_font)

        # Top ingredients
        names = ["Herb", "Crystal", "Frog Eye", "Root", "Essence", "Powder"]
        self.ingredient_buttons = [
            Button(names[i], 60 + i * 150, 150, 130, 48, self.small_font)
            for i in range(4)
        ]

        self.selected_ingredient = None

        # Stations (bottom)
        station_names = ["Retort", "Mortar", "Calcinator", "Cauldron", "Alembic", "Infuser", "Magic Wand"]
        start_x = 40
        spacing = 130
        y_pos = 480
        self.stations = [
            Button(name, start_x + i * spacing, y_pos, 120, 60, self.small_font)
            for i, name in enumerate(station_names)
        ]

        self.max_slots = 3
        self.station_slots = {s.text: [None] * self.max_slots for s in self.stations}

        # Popup
        self.popup_open = False
        self.popup_station = None
        self.popup_rect = None
        self.popup_mix_btn = None
        self.popup_close_btn = None

        self.load_music()

    # ---------------- utils ----------------
    def load_font(self):
        path = os.path.join("assets", "fonts", "MedievalSharp-Regular.ttf")
        return pygame.font.Font(path, 48) if os.path.exists(path) else pygame.font.SysFont(None, 48)

    def load_music(self):
        try:
            path = os.path.join("assets", "sounds", "background.ogg")
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.45)
        except Exception:
            pass
    
    def draw_wrapped_text(self, text, x, y, max_width, font, color):
        words = text.split(' ')
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                surface = font.render(line, True, color)
                self.screen.blit(surface, (x, y))
                y += font.get_height() + 2
                line = word
        if line:
            surface = font.render(line, True, color)
            self.screen.blit(surface, (x, y))



    # ---------------- event handling ----------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return

        if self.state == "menu":
            if self.start_button.is_clicked(event):
                self.state = "mixing"
            return

        if self.state == "mixing":
            # Ingredient clicks should *always* be allowed
            for b in self.ingredient_buttons:
                if b.is_clicked(event):
                    if self.selected_ingredient == b.text:
                        self.selected_ingredient = None
                        print("Deselected ingredient")
                    else:
                        self.selected_ingredient = b.text
                        print(f"Selected ingredient: {self.selected_ingredient}")
                    return

            # If popup open, let both popup + top ingredients work
            if self.popup_open:
                # If click is *inside* popup rect, handle popup events
                if hasattr(event, "pos") and self.popup_rect.collidepoint(event.pos):
                    self._handle_popup_event(event)
                # else, ignore (so you can select ingredients freely)
                return

            # Back button
            if self.back_button.is_clicked(event):
                self.state = "menu"
                return

            # Station click → open popup
            for st in self.stations:
                if st.is_clicked(event):
                    self.open_station_popup(st)
                    return

    # ---------------- popup ----------------
    def _handle_popup_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or not hasattr(event, "pos"):
            return

        pos = event.pos
        if self.popup_close_btn and self.popup_close_btn.rect.collidepoint(pos):
            self.close_popup()
            return
        if self.popup_mix_btn and self.popup_mix_btn.rect.collidepoint(pos):
            self.mix_station(self.popup_station)
            return

        # Click slot to add/remove ingredient
        for i, slot_rect in enumerate(self._slot_rects()):
            if slot_rect.collidepoint(pos):
                slots = self.station_slots[self.popup_station]
                if slots[i]:
                    print(f"Removed {slots[i]} from {self.popup_station} slot {i+1}")
                    slots[i] = None
                else:
                    if self.selected_ingredient:
                        slots[i] = self.selected_ingredient
                        print(f"Placed {self.selected_ingredient} into {self.popup_station} slot {i+1}")
                        self.selected_ingredient = None
                    else:
                        print("No ingredient selected.")
                return

    def open_station_popup(self, station_btn):
        name = station_btn.text
        self.popup_open = True
        self.popup_station = name

        w, h = 320, 220
        screen_w, screen_h = self.screen.get_size()
        x = station_btn.rect.centerx - w // 2
        y = station_btn.rect.top - h - 8
        x = max(8, min(x, screen_w - w - 8))
        y = max(80, min(y, screen_h - h - 8))
        self.popup_rect = pygame.Rect(x, y, w, h)

        self.popup_mix_btn = Button("Mix", x + w - 110, y + h - 56, 90, 40, self.small_font)
        self.popup_close_btn = Button("Close", x + w - 210, y + h - 56, 90, 40, self.small_font)

        print(f"Opened popup for {name}")

    def close_popup(self):
        self.popup_open = False
        self.popup_station = None
        self.popup_rect = None
        self.popup_mix_btn = None
        self.popup_close_btn = None

    def mix_station(self, station_name):
        slots = self.station_slots[station_name]
        ingredients = [s for s in slots if s]
        if not ingredients:
            print(f"No ingredients in {station_name}")
            return
        result = f"Result_of_{station_name}_{'_'.join(ingredients)}"
        print(f"Mixed {ingredients} at {station_name} -> {result}")
        self.station_slots[station_name] = [None] * self.max_slots
        self.close_popup()

    # ---------------- draw ----------------
    def update(self):
        # Add update logic here if needed later
        pass

    def draw(self):
        self.screen.fill((30, 10, 40))

        if self.state == "menu":
            title = self.font.render("Potion Mixer Deluxe", True, (255, 255, 255))
            self.screen.blit(title, (250, 200))
            self.start_button.draw(self.screen)
            return

        # Top: ingredient buttons
        header = self.small_font.render("Ingredients (click to select)", True, (220, 220, 220))
        self.screen.blit(header, (40, 90))


        for b in self.ingredient_buttons:
            if self.selected_ingredient == b.text:
                pygame.draw.rect(self.screen, (255, 215, 0), b.rect.inflate(6, 6), border_radius=8)
            b.draw(self.screen)

        # Back button
        self.back_button.draw(self.screen)

        # Stations
        for st in self.stations:
            st.draw(self.screen)

        # Selected status
        sel_text = f"Selected: {self.selected_ingredient}" if self.selected_ingredient else "Selected: None"
        status = self.small_font.render(sel_text, True, (255, 255, 0))
        self.screen.blit(status, (40, 420))

        if self.popup_open and self.popup_station:
            self._draw_popup()



    def _draw_popup(self):
        rect = self.popup_rect
        pygame.draw.rect(self.screen, (18, 18, 30), rect, border_radius=8)
        pygame.draw.rect(self.screen, (180, 180, 180), rect, 2, border_radius=8)

        title = self.small_font.render(f"{self.popup_station}", True, (255, 255, 255))
        self.screen.blit(title, (rect.x + 12, rect.y + 8))

        slots = self.station_slots[self.popup_station]
        for i, srect in enumerate(self._slot_rects()):
            draw_slot(self.screen, srect.x, srect.y, srect.w, srect.h, self.small_font, content=slots[i])

        if self.popup_mix_btn:
            self.popup_mix_btn.draw(self.screen)
        if self.popup_close_btn:
            self.popup_close_btn.draw(self.screen)

        # Calculate bottom of the last slot
        last_slot_bottom = self._slot_rects()[-1].bottom
        hint_y = last_slot_bottom + 8  

        self.draw_wrapped_text(
            "Select ingredient → click slot to place",
            rect.x + 12,
            hint_y,
            rect.w - 24,
            self.small_font,
            (180, 180, 180)
        )




    def _slot_rects(self):
        rect = self.popup_rect
        x = rect.x + 12
        y = rect.y + 40
        w = rect.w - 24
        h = 38
        gap = 10
        return [pygame.Rect(x, y + i * (h + gap), w, h) for i in range(self.max_slots)]
