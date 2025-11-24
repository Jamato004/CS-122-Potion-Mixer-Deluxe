import pygame
import os
import json
from collections import Counter
from game.ui import Button, Popup, Notification
from game.assets_loader import load_font, load_sound
from game.PotionMixerCommand import Inventory, Mixing, ReservedInventoryView


class MixingScene:
    def __init__(self, screen, small_font):
        self.screen = screen
        self.font = load_font(size=48)
        self.small_font = small_font

        # Sound effects
        self.sfx_click = load_sound("click.wav")
        self.sfx_error = load_sound("error.wav")
        self.sfx_mix = load_sound("mix.wav")
        self.sfx_success = load_sound("success.wav")

        # Inventory + recipe logic
        self.inventory = Inventory()
        self.mixing = Mixing()

        # categories: mapping ingredient_name -> category (solid/liquid/essence/potion)
        self.ingredient_category = {}

        # UI state
        self.max_slots = 3
        self.popup = None
        self.selected_ingredient = None
        self.ingredient_buttons = []

        # Level control
        self.current_level = 1
        self.objective = "Brew something magical!"
        self.level_complete_flag = False
        self.target_potion = None

        # Retry counter
        self.retry_count = 0
        self.retry_button = Button("Retry Level", 420, 550, 160, 50, self.small_font)

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
        self.station_slot_requirements = {
            "Retort": ["potion"],
            "Mortar": ["solid"],
            "Calcinator": ["solid", "solid"],
            "Cauldron": ["liquid", "solid", "essence"],
            "Alembic": ["liquid", "essence"],
            "Infuser": ["solid", "liquid"],
            "Magic Wand": ["essence", "essence"],
        }

        # temporary on-screen notification (message, until_time)
        self.notification = Notification(self.small_font)

    # ---------------- Retry level ----------------
    def retry_level(self):
        # bump counter and fully reload the same level
        self.retry_count += 1
        self.sfx_click.play()
        # close any open popup and selection to avoid weird state
        self.popup = None
        self.selected_ingredient = None
        # reload restores initial ingredients & stations
        self.load_level(self.current_level)

    # ---------------- Check objective ----------------
    def _check_objective(self):
        """If target_potion is owned, mark level complete and celebrate once."""
        if not self.target_potion:
            return
        have = self.inventory.potions.get(self.target_potion, 0)
        if have > 0 and not self.level_complete_flag:
            self.level_complete_flag = True
            self.sfx_success.play()
            self.notification.set(f"Level complete! Brewed {self.target_potion}!", 2.5)

    # ---------------- Load Level ----------------
    def load_level(self, level_number):
        self.inventory = Inventory()           # clears all items
        self.ingredient_category = {}          # forgets old categories
        self.ingredient_buttons = []           # clears buttons
        self.selected_ingredient = None
        self.popup = None
        self.level_complete_flag = False
        self.active_tab = ""
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
        self.target_potion = data.get("target_potion") or data.get("objective_potion")

        # Reset active tab so no ingredients show at start
        self.active_tab = ""

        # Clear ingredient buttons
        self.ingredient_buttons = []

        # Ingredients and categories come from JSON level file
        raw_ings = data.get("ingredients", [])
        self.ingredient_category = {}
        self._check_objective()

        # Fill inventory from JSON; supports either strings or dicts like {name, category, count}
        def to_kind(cat: str) -> str:
            return {
                "liquid": "fluids",
                "solid": "solids",
                "essence": "essences",
                "potion": "potions",
            }.get(cat, "solids")

        for ing in raw_ings:
            if isinstance(ing, dict):
                name = ing.get("name")
                cat = ing.get("category", "solid")
                count = int(ing.get("count", 1))
            else:
                name = str(ing); cat = "solid"; count = 1
            if not name: continue
            self.ingredient_category[name] = cat
            self.inventory.add_to_inventory(name, self._kind_for(cat), count)


        # Stations
        start_x = 40
        spacing = 130
        y_pos = 480
        all_station_names = [
            "Retort", "Mortar", "Calcinator", "Cauldron",
            "Alembic", "Infuser", "Magic Wand"
        ]
        self.stations = [
            Button(name, start_x + i * spacing, y_pos, 120, 60, self.small_font)
            for i, name in enumerate(all_station_names)
        ]

        # Initialize station slots dict with correct number of used slots
        self.station_slots = {}
        for s in self.stations:
            reqs = self.station_slot_requirements.get(s.text, [])
            used_slots = [None for _ in reqs]
            self.station_slots[s.text] = used_slots

        print(f"Loaded Level {self.current_level}: {self.objective}")
        self.layout_ingredient_buttons()


    # ---------------- Layout Ingredients ----------------
    def layout_ingredient_buttons(self):
        """Rebuild ingredient buttons based on the active tab and current inventory."""
        key = self.active_tab
        self.ingredient_buttons = []
        if not key:
            return

        # map tab key -> inventory kind
        key_to_kind = {
            "solid": "solids",
            "liquid": "fluids",
            "essence": "essences",
            "potion": "potions",
        }
        kind = key_to_kind[key]
        items = self.inventory.get_items(kind)

        max_per_row = 6
        row_height = 60
        col_width = 150
        start_x, start_y = 60, 160

        for idx, (name, count) in enumerate(items):
            row = idx // max_per_row
            col = idx % max_per_row
            x = start_x + col * col_width
            y = start_y + row * row_height
            label = f"{name} x{count}"
            btn = Button(label, x, y, 130, 48, self.small_font)
            btn.meta_name = name           # <-- store the real name
            self.ingredient_buttons.append(btn)

    # Utility: map category to inventory kind
    @staticmethod
    def _kind_for(cat: str) -> str:
        return {
            "liquid": "fluids",
            "solid": "solids",
            "essence": "essences",
            "potion": "potions",
        }.get(cat, "solids")

    # ---------------- Event Handling ----------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return

        # Tabs
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, tb in enumerate(self.tab_buttons):
                if tb.is_clicked(event):
                    self.active_tab = self.tab_keys[i]
                    self.layout_ingredient_buttons()
                    return

        # Ingredient selection
        if event.type == pygame.MOUSEBUTTONDOWN:
            for b in self.ingredient_buttons:
                if b.is_clicked(event):
                    real_name = getattr(b, "meta_name", b.text.split(" x")[0])
                    if self.selected_ingredient == real_name:
                        self.selected_ingredient = None
                    else:
                        self.selected_ingredient = real_name
                    return

        # Handle popup if present
        if self.popup:
            pos = getattr(event, "pos", None)
            if pos is not None and self.popup.rect.collidepoint(pos):
                self._handle_popup_event(event)
                return

        # Station clicks (open popup)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for st in self.stations:
                if st.is_clicked(event):
                    self.open_station_popup(st)
                    return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.retry_button.is_clicked(event):
                self.retry_level()
                return

        # Next level button
        if self.level_complete_flag and event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_level_button.is_clicked(event):
                self.load_level(self.current_level + 1)
                return

    # ---------------- Popup Handling ----------------
    def _handle_popup_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or not hasattr(event, "pos"):
            return

        # Close
        if self.popup.close_btn.is_clicked(event):
            self.popup = None
            return

        # Mix
        if self.popup.mix_btn.is_clicked(event):
            self.mix_station(self.popup.station_name)
            return

        # Slot clicks
        pos = event.pos
        for i, slot_rect in enumerate(self.popup.slot_rects()):
            if not slot_rect.collidepoint(pos):
                continue
            station = self.popup.station_name
            reqs = self.station_slot_requirements.get(station, [])
            expected = reqs[i] if i < len(reqs) else None
            slots = self.station_slots[station]

            if slots[i]:
                # remove from slot -> give back to inventory
                name = slots[i]
                cat = self.ingredient_category.get(name, expected or "solid")
                self.inventory.add_to_inventory(name, self._kind_for(cat), 1)
                slots[i] = None
                self.popup.slots = slots
                self.layout_ingredient_buttons()
                self.sfx_click.play()
                continue

            # place selected ingredient
            if not self.selected_ingredient:
                self.notification.set("Select an ingredient first", 1.4)
                self.sfx_error.play()
                return

            sel_name = self.selected_ingredient
            sel_cat = self.ingredient_category.get(sel_name, None)
            if expected and expected != sel_cat:
                self.notification.set(f"Needs {expected}", 1.4)
                self.sfx_error.play()
                return

            kind = self._kind_for(sel_cat or expected or "solid")
            if not self.inventory.check_inventory(sel_name, kind):
                self.notification.set("Out of stock", 1.2)
                self.sfx_error.play()
                return

            # consume and place
            self.inventory.remove_from_inventory(sel_name, kind, 1)
            slots[i] = sel_name
            self.popup.slots = slots
            self.selected_ingredient = None
            self.layout_ingredient_buttons()
            self.sfx_click.play()
            return

    # ---------------- Popup Creation ----------------
    def open_station_popup(self, station_btn):
        name = station_btn.text
        w = 320
        slot_height = 38
        gap = 10
        top_margin = 40
        bottom_margin = 80

        slots = self.station_slots.get(name, [])
        used_slots = len(slots)
        h = top_margin + used_slots * (slot_height + gap) + bottom_margin

        screen_w, screen_h = self.screen.get_size()
        x = station_btn.rect.centerx - w // 2
        y = station_btn.rect.top - h - 8
        x = max(8, min(x, screen_w - w - 8))
        y = max(80, min(y, screen_h - h - 8))

        self.popup = Popup(self.screen, name, x, y, w, h, self.small_font, used_slots)
        self.popup.slots = slots.copy()
        reqs = self.station_slot_requirements.get(name, [None] * used_slots)
        self.popup.expected_types = reqs[:used_slots]

        print(f"Opened popup for {name} with {used_slots} slots")

    # ---------------- Mixing ----------------
    def mix_station(self, station_name):
        slots = self.station_slots[station_name]
        if any(s is None for s in slots):
            self.notification.set("Fill all slots before mixing!", 1.6)
            self.sfx_error.play()
            return

        # Build reserved counts from what’s in the slots
        reserved = {"fluids": Counter(), "solids": Counter(), "essences": Counter(), "potions": Counter()}
        for s in slots:
            cat = self.ingredient_category.get(s, "solid")
            kind = self._kind_for(cat)  # returns "fluids"/"solids"/"essences"/"potions"
            reserved[kind][s] += 1

        inv_view = ReservedInventoryView(self.inventory, reserved)

        # Call the same Mixing methods, but pass the view
        try:
            if station_name == "Mortar":
                result_msg = self.mixing.Mortar(inv_view, slots[0])
            elif station_name == "Calcinator":
                result_msg = self.mixing.Calcinator(inv_view, slots[0], slots[1])
            elif station_name == "Alembic":
                result_msg = self.mixing.Alembic(inv_view, slots[0], slots[1])
            elif station_name == "Infuser":
                result_msg = self.mixing.Infuser(inv_view, slots[0], slots[1])
            elif station_name == "Magic Wand":
                result_msg = self.mixing.Magic_Wand(inv_view, slots[0], slots[1])
            elif station_name == "Cauldron":
                result_msg = self.mixing.Cauldron(inv_view, slots[0], slots[1], slots[2])
            elif station_name == "Retort":
                result_msg = self.mixing.Retort(inv_view, slots[0])
            else:
                result_msg = f"Unknown station: {station_name}"
        except Exception as e:
            result_msg = f"Mixing error: {e}"

        self.sfx_mix.play()

        # Clear used slots (items already removed when slotted; view just made them visible to the mixer)
        self.station_slots[station_name] = [None for _ in slots]
        self.popup = None

        self.notification.set(result_msg, 2.5)
        self.inventory.cleanup()
        self.layout_ingredient_buttons()
        self._check_objective()


    # ---------------- Update ----------------
    def update(self):
        pass

    # ---------------- Draw ----------------
    def draw(self):
        self.screen.fill((30, 10, 40))

        # Objective
        objective_text = self.small_font.render(f"Objective: {self.objective}", True, (255, 255, 255))
        self.screen.blit(objective_text, (500, 50))

        # Tabs
        for i, tb in enumerate(self.tab_buttons):
            key = self.tab_keys[i]
            if self.active_tab == key:
                pygame.draw.rect(self.screen, (70, 70, 120), tb.rect, border_radius=6)
            tb.draw(self.screen)

        # Ingredients
        for b in self.ingredient_buttons:
            real_name = getattr(b, "meta_name", b.text.split(" x")[0])
            if self.selected_ingredient == real_name:
                pygame.draw.rect(self.screen, (255, 215, 0), b.rect.inflate(6, 6), border_radius=8)
            b.draw(self.screen)


        # Stations
        for st in self.stations:
            st.draw(self.screen)

        # Retry
        self.retry_button.draw(self.screen)
        retries_text = self.small_font.render(f"Retries: {self.retry_count}", True, (255, 255, 255))
        self.screen.blit(retries_text, (500, 80))

        # Selected status
        sel_text = f"Selected: {self.selected_ingredient}" if self.selected_ingredient else "Selected: None"
        status = self.small_font.render(sel_text, True, (255, 255, 0))
        self.screen.blit(status, (40, 85))

        # Popup
        if self.popup:
            self.popup.draw()

        # Next Level (kept from original; you may gate this by objective later)
        if self.level_complete_flag:
            self.next_level_button.draw(self.screen)

        # Notification
        self.notification.draw(self.screen)