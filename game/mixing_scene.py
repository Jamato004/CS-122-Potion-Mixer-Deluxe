import pygame
import os
import json
from game.ui import Button, Popup
from game.assets_loader import load_font


class MixingScene:
    def __init__(self, screen, small_font):
        self.screen = screen
        self.font = load_font(size=48)
        self.small_font = small_font
        self.max_slots = 3
        self.popup = None
        self.selected_ingredient = None

        # Level control
        self.current_level = 1
        self.objective = "Brew something magical!"
        self.level_complete_flag = False

        # Buttons
        self.next_level_button = Button("Next Level", 600, 550, 160, 50, self.small_font)

        # Load the first level
        self.load_level(self.current_level)

    # ---------------- Load Level ----------------
    def load_level(self, level_number):
        """Loads a level JSON file and initializes the UI accordingly."""
        level_path = os.path.join("data", "levels", f"level{level_number}.json")
        if not os.path.exists(level_path):
            print(f"Level file not found: {level_path}")
            return

        with open(level_path, "r") as f:
            data = json.load(f)

        self.current_level = data.get("level", level_number)
        self.objective = data.get("objective", "Unknown objective")
        self.level_complete_flag = False
        self.selected_ingredient = None
        self.popup = None

        ingredient_names = data.get("ingredients", [])
        station_names = data.get("stations", [])

        # ---------------- Ingredients ----------------
        self.ingredient_buttons = [
            Button(name, 60 + i * 150, 150, 130, 48, self.small_font)
            for i, name in enumerate(ingredient_names)
        ]

        # ---------------- Stations ----------------
        start_x = 40
        spacing = 130
        y_pos = 480
        self.stations = [
            Button(name, start_x + i * spacing, y_pos, 120, 60, self.small_font)
            for i, name in enumerate(station_names)
        ]
        self.station_slots = {s.text: [None] * self.max_slots for s in self.stations}

        print(f"Loaded Level {self.current_level}: {self.objective}")

    # ---------------- Event Handling ----------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return

        # --- Always allow ingredient selection ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            for b in self.ingredient_buttons:
                if b.is_clicked(event):
                    if self.selected_ingredient == b.text:
                        self.selected_ingredient = None
                        print("Deselected ingredient")
                    else:
                        self.selected_ingredient = b.text
                        print(f"Selected ingredient: {self.selected_ingredient}")
                    return

        # --- If popup exists, only handle events inside it ---
        if self.popup:
            pos = getattr(event, "pos", None)
            if pos is not None and self.popup.rect.collidepoint(pos):
                self._handle_popup_event(event)
                return
            # If clicked outside popup, do not block normal UI actions

        # --- Station clicks (open popup) ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            for st in self.stations:
                if st.is_clicked(event):
                    self.open_station_popup(st)
                    return

        # --- Next Level button ---
        if self.level_complete_flag and self.next_level_button.is_clicked(event):
            self.load_level(self.current_level + 1)
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
                self.popup.slots = slots
                return

    # ---------------- Popup Creation ----------------
    def open_station_popup(self, station_btn):
        name = station_btn.text
        w = 320
        slot_height = 38
        gap = 10
        top_margin = 40
        bottom_margin = 80
        h = top_margin + self.max_slots * (slot_height + gap) + bottom_margin

        screen_w, screen_h = self.screen.get_size()
        x = station_btn.rect.centerx - w // 2
        y = station_btn.rect.top - h - 8
        x = max(8, min(x, screen_w - w - 8))
        y = max(80, min(y, screen_h - h - 8))

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
        self.station_slots[station_name] = [None] * self.max_slots
        self.popup = None

        # Simulate completing the level
        print(f"Level {self.current_level} Complete!")
        self.level_complete_flag = True

    # ---------------- Update ----------------
    def update(self):
        pass

    # ---------------- Draw ----------------
    def draw(self):
        self.screen.fill((30, 10, 40))

        # Objective
        objective_text = self.small_font.render(f"Objective: {self.objective}", True, (255, 255, 255))
        self.screen.blit(objective_text, (500, 50))

        # Ingredients
        header = self.small_font.render("Ingredients (click to select)", True, (220, 220, 220))
        self.screen.blit(header, (40, 90))

        for b in self.ingredient_buttons:
            if self.selected_ingredient == b.text:
                pygame.draw.rect(self.screen, (255, 215, 0), b.rect.inflate(6, 6), border_radius=8)
            b.draw(self.screen)

        # Stations
        for st in self.stations:
            st.draw(self.screen)

        # Selected status
        sel_text = f"Selected: {self.selected_ingredient}" if self.selected_ingredient else "Selected: None"
        status = self.small_font.render(sel_text, True, (255, 255, 0))
        self.screen.blit(status, (40, 110))

        # Popup
        if self.popup:
            self.popup.draw()

        # Next Level button (visible only when complete)
        if self.level_complete_flag:
            self.next_level_button.draw(self.screen)
