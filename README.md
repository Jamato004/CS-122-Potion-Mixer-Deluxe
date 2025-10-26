# Developer Notes
- Game states are managed in `game_manager.py`
- Add new screens or features by creating a new state (e.g., "results", "pause")
- Ingredient and potion logic should go in their respective files under `game/`
- Any new data (recipes, ingredients) can be stored in `data/` as JSON
- little to no changes are needed to `main.py` as it's used to load assets and run the game

# Changelog
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
- data (Data has a higher priority as it's needed for the game to function)
    - ingredients.json list
    - recipes.json list
- game logic
    - ingredient.py
    - mixer.py
    - potion.py
    - ui.py
- implementation
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
