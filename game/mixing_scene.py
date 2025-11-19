# game/mixing_scene.py
import pygame
import os
import json
import time
from game.ui import Button, Popup
from game.assets_loader import load_font


class MixingScene:
    def __init__(self, screen, small_font):
        self.screen = screen
        self.font = load_font(size=48)
        self.small_font = small_font

        # categories: mapping ingredient_name -> category
        # this is filled per-level from JSON but default fallback provided
        self.ingredient_category = {}

        # UI state
        self.max_slots = 3
        self.popup = None
        self.selected_ingredient = None

        # Level control
        self.current_level = 1
        self.objective = "Brew something magical!"
        self.level_complete_flag = False

        # Next level button
        self.next_level_button = Button("Next Level", 600, 550, 160, 50, self.small_font)

        # --- Tabs for categories ---
        self.tab_names = ["Solids", "Liquids", "Essences", "Potions"]
        self.tab_keys = ["solid", "liquid", "essence", "potion"]
        self.active_tab = ""
        self.tab_buttons = []
        tab_x = 40
        for i, name in enumerate(self.tab_names):
            b = Button(name, tab_x + i * 140, 110, 120, 36, self.small_font)
            self.tab_buttons.append(b)

        # station slot rules per station: list of expected categories for each slot
        # use 'any' to accept anything; retort special-case is allowed to accept 'potion' as input
        self.station_slot_requirements = {
            "Retort": ["potion"],  # special: takes a 'potion' like input
            "Mortar": ["solid"],
            "Calcinator": ["solid", "solid", None],  # third slot unused but safe
            "Cauldron": ["liquid", "solid", "essence"],
            "Alembic": ["liquid", "essence", None],
            "Infuser": ["solid", "liquid", None],
            "Magic Wand": ["essence", "essence", None],
        }

        # temporary on-screen notification (message, until_time)
        self.notification = ("", 0.0)

        # Load initial level
        self.load_level(self.current_level)

    # ---------------- Load Level ----------------
    def load_level(self, level_number):
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

        # Ingredients and categories come from JSON level file now
        # JSON expected format: "ingredients": [{"name": "Herb", "category": "solid"}, ...]
        raw_ings = data.get("ingredients", [])
        ingredient_names = []
        self.ingredient_category = {}
        for idx, ing in enumerate(raw_ings):
            if isinstance(ing, dict):
                name = ing.get("name")
                cat = ing.get("category", "solid")
            else:
                # backwards compatibility: string -> default solid
                name = ing
                cat = "solid"
            if not name:
                continue
            ingredient_names.append(name)
            self.ingredient_category[name] = cat

        # Build ingredient buttons based on ingredient_names
        # place according to active tab initially
        self.ingredient_buttons = [
            Button(name, 60 + i * 150, 150, 130, 48, self.small_font)
            for i, name in enumerate(ingredient_names)
        ]

        # Stations loaded from level file (list of names)
        station_names = data.get("stations", [])
        start_x = 40
        spacing = 130
        y_pos = 480
        self.stations = [
            Button(name, start_x + i * spacing, y_pos, 120, 60, self.small_font)
            for i, name in enumerate(station_names)
        ]
        # initialize station slots dict
        self.station_slots = {s.text: [None] * self.max_slots for s in self.stations}

        print(f"Loaded Level {self.current_level}: {self.objective}")

    # ---------------- Notifications ----------------
    def set_notification(self, text, duration=1.6):
        self.notification = (text, time.time() + duration)

    def draw_notification(self):
        text, until = self.notification
        if not text:
            return
        if time.time() > until:
            self.notification = ("", 0.0)
            return
        surf = self.small_font.render(text, True, (255, 200, 100))
        rect = surf.get_rect(center=(self.screen.get_width() // 2, 40))
        # draw semi-transparent background
        bg = pygame.Surface((rect.w + 12, rect.h + 8), pygame.SRCALPHA)
        bg.fill((10, 10, 10, 180))
        self.screen.blit(bg, (rect.x - 6, rect.y - 4))
        self.screen.blit(surf, rect)

    # ---------------- Event Handling ----------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return

        # --- Always allow ingredient selection ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Tabs
            for i, tb in enumerate(self.tab_buttons):
                if tb.is_clicked(event):
                    self.active_tab = self.tab_keys[i]
                    return

            # Ingredient selection: only show those in active tab visually, but selection allowed
            for b in self.ingredient_buttons:
                # only accept click if this ingredient belongs to active tab
                cat = self.ingredient_category.get(b.text, "solid")
                if cat != self.active_tab:
                    continue
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

        # Next level button
        if self.level_complete_flag and event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_level_button.is_clicked(event):
                self.load_level(self.current_level + 1)
                return

    # ---------------- Popup Handling ----------------
    def _handle_popup_event(self, event):
        # react only to mouse clicks inside popup
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
                station = self.popup.station_name
                # Determine expected category for this slot (if mapped)
                reqs = self.station_slot_requirements.get(station, [None]*self.max_slots)
                expected = reqs[i] if i < len(reqs) else None  # could be 'solid','liquid','essence','potion', or None
                # current slot contents
                slots = self.station_slots[station]
                if slots[i]:
                    # remove
                    print(f"Removed {slots[i]} from {station} slot {i+1}")
                    slots[i] = None
                    self.popup.slots = slots
                else:
                    # place selected ingredient if present
                    if not self.selected_ingredient:
                        self.set_notification("Select an ingredient first", 1.4)
                        return
                    # get selected ingredient category
                    sel_cat = self.ingredient_category.get(self.selected_ingredient, None)
                    if expected and expected != "any":
                        # special case: expected 'potion' allowed only if sel_cat == 'potion' (handle later)
                        if expected == "potion":
                            # block unless ingredient is labeled potion (most basic ingredients won't be)
                            self.set_notification("This station needs a potion-like input", 1.6)
                            return
                        if sel_cat != expected:
                            # block placement
                            self.set_notification(f"Cannot place {sel_cat} in this slot (needs {expected})", 1.6)
                            return
                    # allowed: place
                    slots[i] = self.selected_ingredient
                    self.popup.slots = slots
                    print(f"Placed {self.selected_ingredient} into {station} slot {i+1}")
                    # deselect after placing (prevent double placement)
                    self.selected_ingredient = None
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

        # position above station, clamp to screen
        screen_w, screen_h = self.screen.get_size()
        x = station_btn.rect.centerx - w // 2
        y = station_btn.rect.top - h - 8
        x = max(8, min(x, screen_w - w - 8))
        y = max(80, min(y, screen_h - h - 8))

        self.popup = Popup(self.screen, name, x, y, w, h, self.small_font, self.max_slots)
        self.popup.slots = self.station_slots.get(name, [None]*self.max_slots).copy()
        print(f"Opened popup for {name}")

    # ---------------- Mixing ----------------
    def mix_station(self, station_name):
        slots = self.station_slots[station_name]
        ingredients = [s for s in slots if s]
        if not ingredients:
            self.set_notification("No ingredients to mix", 1.4)
            return

        # Here we'd consult the station's CSV-based recipe lookup.
        # For now simulate result and mark level complete.
        result = f"Result_of_{station_name}_" + "_".join(ingredients)
        print(f"Mixed {ingredients} at {station_name} -> {result}")
        self.station_slots[station_name] = [None] * self.max_slots
        self.popup = None

        # Simulate completing the level for testing
        self.level_complete_flag = True
        self.set_notification(f"Level {self.current_level} complete!", 2.0)

    # ---------------- Update ----------------
    def update(self):
        pass

    # ---------------- Draw ----------------
    def draw(self):
        # background cleared by GameManager.draw() usually; do safe fill here
        self.screen.fill((30, 10, 40))

        # Objective
        objective_text = self.small_font.render(f"Objective: {self.objective}", True, (255, 255, 255))
        self.screen.blit(objective_text, (500, 50))

        # Tabs (category tabs)
        for i, tb in enumerate(self.tab_buttons):
            # highlight active tab
            key = self.tab_keys[i]
            if self.active_tab == key:
                pygame.draw.rect(self.screen, (70, 70, 120), tb.rect, border_radius=6)
            tb.draw(self.screen)

        # Ingredients: only draw those matching active tab
        for b in self.ingredient_buttons:
            cat = self.ingredient_category.get(b.text, "solid")
            if cat != self.active_tab:
                continue
            if self.selected_ingredient == b.text:
                pygame.draw.rect(self.screen, (255, 215, 0), b.rect.inflate(6, 6), border_radius=8)
            b.draw(self.screen)

        # Stations
        for st in self.stations:
            st.draw(self.screen)

        # Selected status
        sel_text = f"Selected: {self.selected_ingredient}" if self.selected_ingredient else "Selected: None"
        status = self.small_font.render(sel_text, True, (255, 255, 0))
        self.screen.blit(status, (40, 85))

        # Popup (draw over everything)
        if self.popup:
            self.popup.draw()

        # Next Level button
        if self.level_complete_flag:
            self.next_level_button.draw(self.screen)

        # Notification
        self.draw_notification()
