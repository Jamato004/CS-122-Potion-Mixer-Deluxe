import os
import pygame

# ---------------- Images ----------------
def load_image(name, folder="images"):
    """Load an image from assets and return a Surface with alpha."""
    path = os.path.join("assets", folder, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    return pygame.image.load(path).convert_alpha()


# ---------------- Sounds ----------------
def load_sound(name, folder="sounds"):
    """Load a short sound effect from assets and return a Sound object."""
    path = os.path.join("assets", folder, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Sound not found: {path}")
    return pygame.mixer.Sound(path)


# ---------------- Music ----------------
def load_music(name, folder="sounds", loop=-1, volume=0.2):
    """Load and play background music. Loop=-1 for infinite loop."""
    path = os.path.join("assets", folder, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Music not found: {path}")
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loop)


# ---------------- Fonts ----------------
def load_font(name="MedievalSharp-Regular.ttf", size=48, folder="fonts"):
    """Load a TTF font from assets. Falls back to default font if missing."""
    path = os.path.join("assets", folder, name)
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    else:
        print(f"Font not found: {path}, using default font")
        return pygame.font.SysFont(None, size)
