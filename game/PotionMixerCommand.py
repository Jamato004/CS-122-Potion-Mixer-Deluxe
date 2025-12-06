import pandas as pd
from typing import Dict, List, Tuple
from collections import Counter

class ReservedInventoryView:
    """
    Wraps a real Inventory but 'reserves' some items by kind.
    check_inventory() = base_count + reserved_count
    remove_from_inventory() = consume reserved first, then base
    add_to_inventory() passes through to real inventory
    """
    def __init__(self, base_inventory, reserved_by_kind=None):
        self.base = base_inventory
        self.reserved = reserved_by_kind or {
            "fluids": Counter(),
            "solids": Counter(),
            "essences": Counter(),
            "potions": Counter(),
        }

    def _bucket(self, kind: str):
        # Reuse the real buckets for reads
        return self.base._bucket(kind)

    def add_to_inventory(self, ingredient: str, kind: str, number: int = 1):
        return self.base.add_to_inventory(ingredient, kind, number)

    def remove_from_inventory(self, ingredient: str, kind: str, number: int = 1) -> bool:
        r = self.reserved[kind].get(ingredient, 0)
        if r >= number:
            self.reserved[kind][ingredient] = r - number
            return True
        need = number - r
        if r > 0:
            self.reserved[kind][ingredient] = 0
        return self.base.remove_from_inventory(ingredient, kind, need)

    def check_inventory(self, ingredient: str, kind: str, number: int = 1) -> bool:
        base_have = self._bucket(kind).get(ingredient, 0)
        res_have = self.reserved[kind].get(ingredient, 0)
        return (base_have + res_have) >= number
    def get_items(self, kind: str):
        bucket = self._bucket(kind)
        return [(k, v) for k, v in bucket.items() if v > 0]


    def cleanup(self):
        return self.base.cleanup()

# Inventory that tracks counts by category
class Inventory:
    def __init__(self):
        self.fluids: Dict[str, int] = {}
        self.solids: Dict[str, int] = {}
        self.essences: Dict[str, int] = {}
        self.potions: Dict[str, int] = {}


    def debug_counts(self):
        # safe snapshot for prints/logs
        return {
            "fluids": dict(self.fluids),
            "solids": dict(self.solids),
            "essences": dict(self.essences),
            "potions": dict(self.potions),
        }

    def _bucket(self, kind: str) -> Dict[str, int]:
        kind = kind.lower()
        if kind in ("fluid", "fluids", "liquid", "liquids"):
            return self.fluids
        if kind in ("solid", "solids"):
            return self.solids
        if kind in ("essence", "essences"):
            return self.essences
        if kind in ("potion", "potions"):
            return self.potions
        raise ValueError(f"Unknown kind: {kind}")

    def add_to_inventory(self, ingredient: str, kind: str, number: int = 1) -> None:
        bucket = self._bucket(kind)
        bucket[ingredient] = bucket.get(ingredient, 0) + max(0, int(number))

    def remove_from_inventory(self, ingredient: str, kind: str, number: int = 1) -> bool:
        bucket = self._bucket(kind)
        if bucket.get(ingredient, 0) >= number:
            bucket[ingredient] -= number
            return True
        return False

    def check_inventory(self, ingredient: str, kind: str, number: int = 1) -> bool:
        bucket = self._bucket(kind)
        return bucket.get(ingredient, 0) >= number

    def get_items(self, kind: str) -> List[Tuple[str, int]]:
        bucket = self._bucket(kind)
        return [(k, v) for k, v in bucket.items() if v > 0]

    def cleanup(self) -> None:
        for bucket in (self.fluids, self.solids, self.essences, self.potions):
            to_del = [k for k, v in bucket.items() if v <= 0]
            for k in to_del:
                del bucket[k]


def clean_up(inventory: Inventory):
    inventory.cleanup()


class Mixing:
    def __init__(self):
        # Match the lowercase "data/" path used elsewhere in the project
        self.retort_recipes = pd.read_csv("data/Retort.csv")
        self.mortar_recipes = pd.read_csv("data/Mortar.csv")
        self.calc_recipes = pd.read_csv("data/Calcinator.csv")
        self.alembic_recipes = pd.read_csv("data/Alembic.csv")
        self.infuser_recipes = pd.read_csv("data/Infuser.csv")
        self.wand_recipes = pd.read_csv("data/Magic_Wand.csv")
        self.cauldron_recipes = pd.read_csv("data/Cauldron.csv")

    # Helper to pull first value from a column if a mask matches any rows
    @staticmethod
    def _first(df: pd.DataFrame, col: str):
        if df.empty:
            return None
        try:
            return df.iloc[0][col]
        except Exception:
            return None

    # NOTE: per UI rules, Retort takes a POTION-like input and yields essences
    def Retort(self, inventory: Inventory, potion: str) -> str:
        if not inventory.check_inventory(potion, "potions"):
            return "You don't have that potion."
        inventory.remove_from_inventory(potion, "potions", 1)
        recipe = self.retort_recipes[self.retort_recipes["Input"] == potion]
        if recipe.empty:
            return "The retort failed to produce anything..."

        outputs = []
        for col in ("Output1", "Output2", "Output3"):
            out = self._first(recipe, col)
            if out and str(out) != "None":
                inventory.add_to_inventory(out, "essences", 1)
                outputs.append(out)
        clean_up(inventory)
        return f"The retort produced {outputs} from {potion}!"

    def Mortar(self, inventory: Inventory, solid: str) -> str:
        if not inventory.check_inventory(solid, "solids"):
            return "You don't have that solid."
        inventory.remove_from_inventory(solid, "solids", 1)
        recipe = self.mortar_recipes[self.mortar_recipes["Solid"] == solid]
        if recipe.empty:
            return f"You couldn't grind up the {solid}..."
        output = self._first(recipe, "Output")
        if output:
            inventory.add_to_inventory(output, "solids", 1)
            clean_up(inventory)
            return f"You ground the {solid} into {output}!"
        return f"You couldn't grind up the {solid}..."

    def Calcinator(self, inventory: Inventory, solid1: str, solid2: str) -> str:
        if not (inventory.check_inventory(solid1, "solids") and inventory.check_inventory(solid2, "solids")):
            return "You lack the required solids."
        inventory.remove_from_inventory(solid1, "solids", 1)
        inventory.remove_from_inventory(solid2, "solids", 1)
        mask = (self.calc_recipes["Solid1"] == solid1) & (self.calc_recipes["Solid2"] == solid2)
        recipe = self.calc_recipes[mask]
        if recipe.empty:
            return "The calcinator created useless ash..."
        output = self._first(recipe, "Output")
        if output:
            inventory.add_to_inventory(output, "solids", 1)
            clean_up(inventory)
            return f"You refined {solid1} and {solid2} into {output}!"
        return "The calcinator created useless ash..."

    def Alembic(self, inventory: Inventory, liquid: str, essence: str) -> str:
        if not (inventory.check_inventory(liquid, "fluids") and inventory.check_inventory(essence, "essences")):
            return "You lack the required liquid/essence."
        inventory.remove_from_inventory(liquid, "fluids", 1)
        inventory.remove_from_inventory(essence, "essences", 1)
        mask = (self.alembic_recipes["Liquid1"] == liquid) & (self.alembic_recipes["Essence1"] == essence)
        recipe = self.alembic_recipes[mask]
        if recipe.empty:
            return "The alembic fills with white smoke. The reaction must not have worked..."
        output = self._first(recipe, "Output")
        if output:
            inventory.add_to_inventory(output, "fluids", 1)
            clean_up(inventory)
            return f"You transmuted {liquid} into {output} with {essence}!"
        return "The alembic fills with white smoke. The reaction must not have worked..."

    def Infuser(self, inventory: Inventory, solid: str, liquid: str) -> str:
        if not (inventory.check_inventory(solid, "solids") and inventory.check_inventory(liquid, "fluids")):
            return "You lack the required solid/liquid."
        inventory.remove_from_inventory(solid, "solids", 1)
        inventory.remove_from_inventory(liquid, "fluids", 1)
        mask = (self.infuser_recipes["Solid1"] == solid) & (self.infuser_recipes["Liquid1"] == liquid)
        recipe = self.infuser_recipes[mask]
        if recipe.empty:
            return "The reaction failed and resulted in useless sludge..."
        output = self._first(recipe, "Output")
        if output:
            inventory.add_to_inventory(output, "fluids", 1)
            clean_up(inventory)
            return f"You infused {solid} into {liquid} and created {output}!"
        return "The reaction failed and resulted in useless sludge..."

    def Magic_Wand(self, inventory: Inventory, essence1: str, essence2: str) -> str:
        if not (inventory.check_inventory(essence1, "essences") and inventory.check_inventory(essence2, "essences")):
            return "You lack the required essences."
        inventory.remove_from_inventory(essence1, "essences", 1)
        inventory.remove_from_inventory(essence2, "essences", 1)
        mask = (self.wand_recipes["Essence1"] == essence1) & (self.wand_recipes["Essence2"] == essence2)
        recipe = self.wand_recipes[mask]
        if recipe.empty:
            return "The magic wand made the essences disappear..."
        output = self._first(recipe, "Output")
        if output:
            inventory.add_to_inventory(output, "essences", 1)
            clean_up(inventory)
            return f"The magic wand combined {essence1} and {essence2} into {output}!"
        return "The magic wand made the essences disappear..."

    def Cauldron(self, inventory: Inventory, liquid: str, solid: str, essence: str) -> str:
        ok = (
            inventory.check_inventory(liquid, "fluids")
            and inventory.check_inventory(solid, "solids")
            and inventory.check_inventory(essence, "essences")
        )
        if not ok:
            return "You lack the required liquid/solid/essence."
        inventory.remove_from_inventory(liquid, "fluids", 1)
        inventory.remove_from_inventory(solid, "solids", 1)
        inventory.remove_from_inventory(essence, "essences", 1)
        mask = (
            (self.cauldron_recipes["Liquid"] == liquid)
            & (self.cauldron_recipes["Solid"] == solid)
            & (self.cauldron_recipes["Essence"] == essence)
        )
        recipe = self.cauldron_recipes[mask]
        if recipe.empty:
            return "This looks more like a soup than a potion..."
        output = self._first(recipe, "Output")
        if output:
            inventory.add_to_inventory(output, "potions", 1)
            clean_up(inventory)
            return f"You successfully brewed a {output}!"
        return "This looks more like a soup than a potion..."