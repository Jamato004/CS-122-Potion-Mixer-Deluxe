class Mixer:
    """Handles logic for combining ingredients to create potions."""
    def __init__(self):
        self.ingredients = []

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)

    def mix(self):
        """Placeholder for mixing logic."""
        if not self.ingredients:
            return None
        # Dummy output
        return f"Mixed {len(self.ingredients)} ingredients!"
