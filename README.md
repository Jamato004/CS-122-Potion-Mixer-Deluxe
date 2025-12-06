# Instruction to run game
## Option 1 (ngl this is my first time making a .exe so not sure if it'll work as intended)
1. Download and extract the zip
2. Run the application `dist/PotionMixer/PotionMixer.exe`

## Option 2
1. Download and extract the zip
2. In your coding software of choice
    - VS code
    - Pycharm
3. Install dependencies in the terminal
```
pip install requirements.txt
```
4. run `main.py`

# Recepies for testing
1. Level 1
    - Mortor (Dragon Scale) -> Dragonscale Powder
    - Infuser (Dragonscale Powder, Ethanol) -> Raging Mixture
    - Cauldron (Raging Mixture, Manticore Honey, Essence of Destruction) -> Potion of Might
2. Level 2
    - Mortar (Golem Heart) -> Anima Dust
    - Infuser (Anima Dust, Water) -> Serene Fluid
    - Cauldron (Serene Fluid, Silicate Powder, Essence of Water) -> Potion of Waterbreathing


# Changelog
## 12/6 Changes
- fixed bug where level stats saved when player mixed and not on level completion
- removed files and code that weren't used
- fixed nan handling specifically for essences
- changed retort's input to liquid as the potion input was due to miscommunication
- created a .exe file so you can just run the application
## 12/1 Changes
- added a reset progress button
- removed the potions from the levels from testing
## 11/26 Changes
- fixed all bugs mentioned in 11/25
- `level_stats.json` is now updating once level completion.
- want to lock levels so you must complete the previous level
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

# Project Structure
```
CS-122-Potion-Mixer-Deluxe/
│
├── main.py
├── game/
│   ├── game_manager.py
│   ├── level_select_scene.py
│   ├── mixing_scene.py
│   ├── mixing_level.py
│   ├── mixing_popup.py
│   ├── ui.py
│   ├── PotionMixerCommand.py
│   └── assets_loader.py
│
├── assets/
│   ├── fonts/
│   └── sounds/
│
├── data/
│   ├── levels/
│   ├── level_stats.json
│   ├── Retort.csv
│   ├── Calcinator.csv
│   └── ...
│
├── requirements.txt
└── README.md

```
