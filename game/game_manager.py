import pygame
import os
from game.ui import Button, draw_slot, Popup
from game.assets_loader import load_image, load_sound, load_music, load_font

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = "menu"
        self.font = load_font(size=48)
        self.small_font = pygame.font.Font(None, 28)

        # ---------------- Menu Buttons ----------------
        self.start_button = Button("Start Mixing", 360, 340, 240, 60, self.small_font)
        self.back_button = Button("Back to Menu", 20, 20, 200, 50, self.small_font)

        # ---------------- Ingredients ----------------
        names = ["Herb", "Crystal", "Frog Eye", "Root", "Essence", "Powder"]
        self.ingredient_buttons = [
            Button(names[i], 60 + i * 150, 150, 130, 48, self.small_font)
            for i in range(6)
        ]
        self.selected_ingredient = None

        # ---------------- Stations ----------------
        station_names = ["Retort", "Mortar", "Calcinator", "Cauldron",
                         "Alembic", "Infuser", "Magic Wand"]
        start_x = 40
        spacing = 130
        y_pos = 480
        self.stations = [
            Button(name, start_x + i * spacing, y_pos, 120, 60, self.small_font)
            for i, name in enumerate(station_names)
        ]
        self.max_slots = 3
        self.station_slots = {s.text: [None] * self.max_slots for s in self.stations}

        # ---------------- Popup ----------------
        self.popup = None

        load_music("background.ogg")

    # ---------------- Event Handling ----------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return

        if self.state == "menu":
            if self.start_button.is_clicked(event):
                self.state = "mixing"
            return

        if self.state == "mixing":
            # Ingredient selection always works
            for b in self.ingredient_buttons:
                if b.is_clicked(event):
                    if self.selected_ingredient == b.text:
                        self.selected_ingredient = None
                        print("Deselected ingredient")
                    else:
                        self.selected_ingredient = b.text
                        print(f"Selected ingredient: {self.selected_ingredient}")
                    return

            # If popup is open, delegate event handling
            if self.popup:
                self._handle_popup_event(event)
                return

            # Back to menu
            if self.back_button.is_clicked(event):
                self.state = "menu"
                return

            # Station click → open popup
            for st in self.stations:
                if st.is_clicked(event):
                    self.open_station_popup(st)
                    return

    # ---------------- Popup Handling ----------------
    def _handle_popup_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or not hasattr(event, "pos"):
            return

        pos = event.pos
        # Close button
        if self.popup.close_btn.is_clicked(event):
            self.popup = None
            return
        # Mix button
        if self.popup.mix_btn.is_clicked(event):
            self.mix_station(self.popup.station_name)
            return
        # Slot clicks
        for i, slot_rect in enumerate(self.popup.slot_rects()):
            if slot_rect.collidepoint(pos):
                slots = self.station_slots[self.popup.station_name]
                if slots[i]:
                    print(f"Removed {slots[i]} from {self.popup.station_name} slot {i+1}")
                    slots[i] = None
                else:
                    if self.selected_ingredient:
                        slots[i] = self.selected_ingredient
                        print(f"Placed {self.selected_ingredient} into {self.popup.station_name} slot {i+1}")
                        self.selected_ingredient = None
                    else:
                        print("No ingredient selected.")
                # Update popup slots
                self.popup.slots = slots
                return

    def open_station_popup(self, station_btn):
        name = station_btn.text
        w = 320
        slot_height = 38
        gap = 10
        top_margin = 40       # space for title
        bottom_margin = 80    # space for hint + buttons
        h = top_margin + self.max_slots * (slot_height + gap) + bottom_margin

        screen_w, screen_h = self.screen.get_size()
        x = station_btn.rect.centerx - w // 2
        y = station_btn.rect.top - h - 8
        x = max(8, min(x, screen_w - w - 8))
        y = max(80, min(y, screen_h - h - 8))

        # Initialize popup with current station slots
        self.popup = Popup(self.screen, name, x, y, w, h, self.small_font, self.max_slots)
        self.popup.slots = self.station_slots[name].copy()
        print(f"Opened popup for {name}")

    # ---------------- Mixing ----------------
    def mix_station(self, station_name):
        slots = self.station_slots[station_name]
        ingredients = [s for s in slots if s]
        if not ingredients:
            print(f"No ingredients in {station_name}")
            return
        result = f"Result_of_{station_name}_{'_'.join(ingredients)}"
        print(f"Mixed {ingredients} at {station_name} -> {result}")
        # Clear station
        self.station_slots[station_name] = [None] * self.max_slots
        self.popup = None

    # ---------------- Draw ----------------
    def update(self):
        # placeholder if needed later
        pass

    def draw(self):
        self.screen.fill((30, 10, 40))

        if self.state == "menu":
            title = self.font.render("Potion Mixer Deluxe", True, (255, 255, 255))
            self.screen.blit(title, (250, 200))
            self.start_button.draw(self.screen)
            return

        # Ingredients
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
        self.screen.blit(status, (40, 110))

        # Draw popup if open
        if self.popup:
            self.popup.draw()
