import os, json
from game.PotionMixerCommand import Inventory

def load_level_data(level_number):
    level_path = os.path.join("data", "levels", f"level{level_number}.json")
    if not os.path.exists(level_path):
        print(f"Level file not found: {level_path}")
        return None

    with open(level_path, "r") as f:
        data = json.load(f)

    return data

def build_inventory_from_level(data):
    inv = Inventory()
    ingredient_category = {}

    raw_ings = data.get("ingredients", [])

    def kind_for(cat: str) -> str:
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
        if not name:
            continue
        ingredient_category[name] = cat
        inv.add_to_inventory(name, kind_for(cat), count)

    return inv, ingredient_category
