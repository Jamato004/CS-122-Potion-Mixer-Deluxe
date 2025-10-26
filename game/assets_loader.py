import os
import pygame

def load_image(name, folder="images"):
    path = os.path.join("assets", folder, name)
    return pygame.image.load(path).convert_alpha()

def load_sound(name, folder="sounds"):
    path = os.path.join("assets", folder, name)
    return pygame.mixer.Sound(path)
