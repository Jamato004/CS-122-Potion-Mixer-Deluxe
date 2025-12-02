import os, json, pygame
from game.ui import Button
from game.assets_loader import load_font

class LevelSelectScene:
    def __init__(self, screen, small_font, levels_path="data/levels"):
        self.screen = screen
        self.font = load_font(size=48)
        self.small_font = small_font
        self.levels_path = levels_path

        # Buttons and data
        self.level_buttons = []
        self.back_button = Button("Back", 20, 20, 120, 40, small_font)
        self.reset_button = Button("Reset Stats", 20, 70, 200, 40, small_font)

        # put stats next to level JSONs
        self.stats_path = os.path.join("data", "level_stats.json")
        self.stats = self._load_stats()

        # Load all level files
        self.level_files = sorted(
            [f for f in os.listdir(levels_path) if f.lower().endswith(".json")]
        )
        self._create_buttons()

    # --- Persistent stats helpers ---
    def _load_stats(self):
        if os.path.exists(self.stats_path):
            with open(self.stats_path, "r") as f:
                data = json.load(f)
            # make sure it has the expected structure
            if not isinstance(data, dict):
                data = {}
            if "levels" not in data:
                levels = {}
                for k, v in data.items():
                    levels[str(k)] = {"best_retries": v}
                data = {"levels": levels}
            return data
        # default structure
        return {"levels": {}}

    def _save_stats(self):
        os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)
        with open(self.stats_path, "w") as f:
            json.dump(self.stats, f, indent=2)

    def update_best_retry(self, level_num, retry_count):
        """Record best (lowest) retry count for a level."""
        key = str(level_num)
        level_info = self.stats["levels"].get(key, {})
        best = level_info.get("best_retries")
        if best is None or retry_count < best:
            level_info["best_retries"] = retry_count
            self.stats["levels"][key] = level_info
            self._save_stats()
            self._create_buttons()  # refresh labels

    # allow GameManager to manually refresh after other changes if needed
    def refresh(self):
        self._create_buttons()

    # --- UI ---
    def _create_buttons(self):
        self.level_buttons.clear()
        start_x, start_y = 120, 160
        col_width, row_height = 220, 70
        per_row = 3

        for idx, filename in enumerate(self.level_files):
            level_num = int("".join([c for c in filename if c.isdigit()]) or 0)
            label = f"Level {level_num}"

            key = str(level_num)
            level_info = self.stats["levels"].get(key, {})
            best = level_info.get("best_retries")

            if best is not None:
                label += f" (Best {best})"

            row = idx // per_row
            col = idx % per_row
            x = start_x + col * col_width
            y = start_y + row * row_height
            self.level_buttons.append(Button(label, x, y, 200, 50, self.small_font))

    def reset_stats(self):
        # Completely wipe stats
        self.stats = {"levels": {}}
        self._save_stats()
        self._create_buttons()
        print("Level stats reset!")

    # --- Event ---
    def handle_event(self, event, game_manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(event):
                game_manager.state = "menu"
                return
            
            if self.reset_button.is_clicked(event):
                self.reset_stats()
                return

            for idx, btn in enumerate(self.level_buttons):
                if btn.is_clicked(event):
                    filename = self.level_files[idx]
                    level_num = int("".join([c for c in filename if c.isdigit()]) or 0)
                    game_manager.start_level(level_num)
                    return

    # --- Draw ---
    def draw(self):
        self.screen.fill((20, 10, 30))
        title = self.font.render("Select a Level", True, (255, 255, 255))
        self.screen.blit(title, (260, 60))

        for btn in self.level_buttons:
            btn.draw(self.screen)

        self.back_button.draw(self.screen)
        self.reset_button.draw(self.screen)