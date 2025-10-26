class Potion:
    """Represents a potion created from ingredients."""
    def __init__(self, name, color, effect):
        self.name = name
        self.color = color
        self.effect = effect

    def __repr__(self):
        return f"<Potion {self.name}: {self.effect}>"
