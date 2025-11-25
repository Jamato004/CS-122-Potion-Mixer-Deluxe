# Install instruction
1. Download and extract the zip
2. Install dependencies
```
pip install requirements.txt
```
3. run `main.py`

# Developer Notes
- Game states are managed in `game_manager.py`
- Add new screens or features by creating a new state (e.g., "results", "pause")
- Ingredient and potion logic should go in their respective files under `game/`
- Game logic to be implemented in `mixing_scene.py`
- Any new data (recipes, ingredients) can be stored in `data/` as JSON
- little to no changes are needed to `main.py` as it's used to load assets and run the game

# Changelog
## 11/25 Changes
- levels are now being developed
    - 7 levels total
    - 6 completed
- Bugs to be fixed
    - stations do give an output and shows up in inventory, but that ingredient has no category
    - names of ingredients are long and need to be wrapped
    - names of potions can be shortened removing "Potion of"
    - names of essences can be shortened removing "Essence of"
    - `level_stats.json` can be looked at further as it's kinda weird with how it updates. Also maybe have save files?
## 11/24 Changes
- updated csvs
- cleaned `mixing_scene.py` to be shorter
    - moved level loading to a different file `mixing_level.py`
    - moved popup handling to a different file `mixing_popup.py`
- delete `tests/`, `mixer.py`, `potion.py`, `ingredient.py` as they were unused
- moved `level_stats.json` out of `levels/` as it was causing it to show up in level select
## 11/23 Changes
- game logic added `PotionMixerCommand.py`
- tweaked levels
    - removed the stations
    - added a counter for ingredients
    - added the potion requirement to finish level
- added a retry counter and button
- added logic for level completion
- added counters for ingredients
- added level select screen
## 11/19 Changes
- stations now have the correct amomunt of slots
- station slots have the ingredient type needed
- stations will only mix once all the slots are filled
- ingredients are not pre-loaded allowing them to load individually per type
- moved code for notifactions to `ui.py`
## 11/18 Changes
- added ingredient type buttons that show ingredients of that type
- added notification on level completion
- changed stations to only accept applicable ingredients
    - also notifies players if the ingredient is wrong and what SHOULD go in that slot
- TODO
    - ingredients are still loaded in order so theres still a max of 6 total ingredients
    - ingredients should be loaded over the unloaded ingredients so total ingredients can reach 18, maybe 24 if we include a potions tab
    - stations should have little labels in their input areas instead of just "empty"
## 11/1 Changes
- added levels and temporary files to test levels
- restructured `game_manager.py` so it will only be handling game states
- moved the mixing scene logic from `game_manager.py` to a new file `mixing_scene.py`
## 10/31 Changes
- Added mixing screen
    - currently uses hardcoded ingredients
    - I'm assuming that the stations in the excel file will be in every level
    - might need to move the code for mixing to a new file so `game_manager.py` doesn't get too big as code for doing the levels needs to be added
- changes in `ui.py`
    - add `def draw_slot(...)` to help with the station ui
    - add `image=None` to the `__init__` to render images
- added a test.png into `assets/images/ui`
    - used just to see how images work with buttons
- changed `background.ogg` music to a smaller song
- moved the "Selected:" text up so it won't be covered by the popup
- moved the popup stuff into `ui.py`
## 10/26 Changes
- WIP window for the game
- added background music in `game_manager.py` using `background.ogg` 
- `assets_loader.py` finished (easier to call on assets)
- added placeholder code to `ingredient.py`/`mixer.py`/`potion.py`
- added button class for `ui.py`
- `game_manager.py` has simple loads for main menu and "mixing" screen
- added `credits.txt` to `assets/` 
- added small list for `ingredients.json` and `recipes.json`
- added assumed imports for `test_mixer.py` and `test_potion.py`

---

# TODO
- data (Adding the csvs from the excel)
    - ingredients.json list
    - recipes.json list
- game logic
    - ingredient.py
    - mixer.py
    - potion.py
- implementation (Missing: sprites, level select, options menu, win/lose screens)
    - game_manager
    - main.py

---

# Project Structure
```
CS-122-POTION-MIXER-DELUXE/  
│  
├── main.py                   # Entry point of the game  
│  
├── game/  
│   ├── __init__.py  
│   ├── game_manager.py       # Handles game states (menu, mixing, results)  
│   ├── mixer.py              # Core logic: mixing ingredients, determining outcomes  
│   ├── potion.py             # Potion class (name, color, effect)  
│   ├── ingredient.py         # Ingredient class (name, property, color, etc.)  
│   ├── ui.py                 # Handles buttons, text, and other GUI elements  
│   └── assets_loader.py      # Loads images, sounds, fonts  
│  
├── assets/  
│   ├── images/  
│   │   ├── ingredients/      # Ingredient sprites  
│   │   ├── potions/          # Potion result images  
│   │   └── ui/               # Buttons, backgrounds  
│   ├── sounds/  
│   │   ├── background.ogg
│   │   ├── mix.wav  
│   │   └── success.wav  
│   └── fonts/  
│       └── MedievalSharp-Regular.ttf  
│
├── data/  
│   ├── levels/
│   │   ├── level1.json
│   │   ├── level2.json
│   │   └── level3.json
│   ├── ingredients.json      # Ingredient definitions (e.g. {"herb": {"color": "green"}})  
│   └── recipes.json          # Potion recipes and results  
│  
├── tests/  
│   ├── test_mixer.py         # Unit tests for mixing logic  
│   └── test_potion.py  
│  
├── requirements.txt          # Dependencies (e.g. pygame)  
└── README.md                 # Setup instructions, description  
```
