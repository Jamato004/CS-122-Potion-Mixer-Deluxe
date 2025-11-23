import pandas as pd

#creates inventory object with methods to add and remove and check if items are in it. the "kind" variable is for specifying which kind of ingredient it belongs to#
class Inventory:
    def __init__(self):
        self.fluids = {}
        self.solids = {}
        self.essences = {}
        self.potions = {}
    def add_to_inventory(self, ingredient, kind, number):
        presence = False
        if ingredient in self.kind.keys():
            self.kind[ingredient] += number
            presence = True
        if presence == False:
            self.kind[ingredient] = number
    def remove_from_inventory(self, ingredient, kind, number):
        if ingredient in self.kind.keys():
            if self.kind[ingredient] >= number:
                self.kind[ingredient] -= number
    def check_inventory(self, ingredient, kind):
        if ingredient in self.kind.keys() and self.kind[ingredient] >= 1:
            return True
        else:
            return False

#removes any empty entries in the inventory. not necessarily needed, but already implemented and makes things cleaner"
def clean_up(inventory):
    for k,v in inventory.fluids:
        if v == 0:
            del inventory.fluids[k]
            
    for k,v in inventory.solids:
        if v == 0:
            del inventory.solids[k]

    for k,v in inventory.essences:
        if v == 0:
            del inventory.essences[k]



class Mixing:
    def __init__(self):
        self.retort_recipes = pd.read_csv("Retort.csv")
        self.mortar_recieps = pd.read_csv("Mortar.csv")
        self.calc_recipes = pd.read_csv("Calcinator.csv")
        self.alembic_recipes = pd.read_csv("Alembic.csv")
        self.infuser_recipes = pd.read_csv("Infuser.csv")
        self.wand_recipes = pd.read_csv("Magic_Wand.csv")
        self.cauldron_recipes = pd.read_csv("Cauldron.csv")

    def Retort(self, inventory, liquid):
        if inventory.check_inventory(liquid, "fluids") == True:
            inventory.remove_from_inventory(liquid, "fluids", 1)
            recipe = self.retort_recipes[self.retort_recipes["Input"] == liquid]
            if recipe.empty == False:
                output1 = recipe.loc[1, "Output1"]
                output2 = recipe.loc[1, "Output2"]
                output3 = recipe.loc[1, "Output3"]
                outputs = [output1]
                inventory.add_to_inventory(output1, "essences", 1)
                if output2 != "None":
                    inventory.add_to_inventory(output2, "essences", 1)
                    outputs.append(output2)
                if output3 != "None":
                    inventory.add_to_inventory(output3, "essences", 1)
                    outputs.append(output3)
                clean_up(inventory)
                return f"The retort produced {outputs} from {liquid}!"
            else:
                return "The retort failed to produce anything..."
        
    def Mortar(self, inventory, solid):
        if inventory.check_inventory(solid, "solids") == True:
            inventory.remove_from_inventory(solid, "solids", 1)
            recipe = self.mortar_recieps[self.mortar_recieps["Solid"] == solid]
            if recipe.empty == False:
                output = recipe.loc[1, "Output"]
                inventory.add_to_inventory(output, "solids", 1)
                clean_up(inventory)
                return f"You grinded the {solid} into {output}!"
            else:
                return f"You couldn't grind up the {solid}..."

    def Calcinator(self, inventory, solid1, solid2):
        if inventory.check_inventory(solid1, "solids") == True and inventory.check_inventory(solid2, "solids") == True:
            inventory.remove_from_inventory(solid1, "solids", 1)
            inventory.remove_from_inventory(solid2, "solids", 1)
            recipe = self.calc_recipes[self.calc_recipes["Solid1"] == solid1 & self.calc_recipes["Solid2"] == solid2]
            if recipe.empty == False:
                output = recipe.loc[1, "Output"]
                inventory.add_to_inventory(output, "solids", 1)
                clean_up(inventory)
                return f"You refined {solid1} and {solid2} into {output}!"
            else:
                return f"The calcinator created useless ash..."

    def Alembic(self, inventory, liquid, essence):
        if inventory.check_inventory(liquid, "fluids") == True and inventory.check_inventory(essence, "essences") == True:
            inventory.remove_from_inventory(liquid, "fluids", 1)
            inventory.remove_from_inventory(essence, "essences", 1)
            recipe = self.alembic_recipes[self.alembic_recipes["Liquid1"] == liquid & self.alembic_recipes["Essence1"] == essence]
            if recipe.empty == False:
                output = recipe.loc[1, "Output"]
                inventory.add_to_inventory(output, "fluids", 1)
                clean_up(inventory)
                return f"You transmuted {liquid} into {output} with {essence}!"
            else:
                return f"The alembic fills with white smoke. The reaction must not have worked..."

    def Infuser(self, inventory, solid, liquid):
        if inventory.check_inventory(solid, "solids") == True and inventory.check_inventory(liquid, "fluids") == True:
            inventory.remove_from_inventory(solid, "solids", 1)
            inventory.remove_from_inventory(liquid, "fluids", 1)
            recipe = self.infuser_recipes[self.alembic_recipes["Solid1"] == solid & self.infuser_recipes["Liquid1"] == liquid]
            if recipe.empty == False:
                output = recipe.loc[1, "Output"]
                inventory.add_to_inventory(output, "fluids", 1)
                clean_up(inventory)
                return f"You infused {solid} into {liquid} and created {output}!"
            else:
                return f"The reaction failed and resulted in useless sludge..."

    def Magic_Wand(self, inventory, essence1, essence2):
        if inventory.check_inventory(essence1, "essences") == True and inventory.check_inventory(essence2, "essences") == True:
            inventory.remove_from_inventory(essence1, "essences", 1)
            inventory.remove_from_inventory(essence2, "essences", 1)
            recipe = self.wand_recipes[self.wand_recipes["Essence1"] == essence1 & self.wand_recipes["Essence2"] == essence2]
            if recipe.empty == False:
                output = recipe.loc[1, "Output"]
                inventory.add_to_inventory(output, "essences", 1)
                clean_up(inventory)
                return f"The magic wand combined {essence1} and {essence2} into {output}!"
            else:
                return f"The magic wand made the essences disappear..."


    def Cauldron(self, inventory, liquid, solid, essence):
        if inventory.check_inventory(liquid, "fluids") == True and inventory.check_inventory(solid, "solids") == True and inventory.check_inventory(essence, "essences") == True:
            inventory.remove_from_inventory(liquid, "fluids", 1)
            inventory.remove_from_inventory(solid, "solids", 1)
            inventory.remove_from_inventory(essence, "essences", 1)
            recipe = self.cauldron_recipes[self.cauldron_recipes["Liquid"] == liquid & self.cauldron_recipes["Solid"] == solid & self.cauldron_recipes["Essence"] == essence]
            if recipe.empty == False:
                output = recipe.loc[1, "Output"]
                inventory.add_to_inventory(output, "potions", 1)
                clean_up(inventory)
                return f"You successfully brewed a {output}!"
            else:
                return f"This looks more like a soup than a potion..."

            

