class Ingredient:
    """Represents an ingredient that can be used in potion mixing."""
    def __init__(self, name, color, effect=None):
        self.name = name
        self.color = color
        self.effect = effect or "Unknown"

    def __repr__(self):
        return f"<Ingredient {self.name} ({self.color})>"
