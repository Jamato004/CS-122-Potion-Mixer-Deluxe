import pygame

class Button:
    def __init__(self, text, x, y, width, height, font,
                 color=(160,160,160), hover_color=(200,200,200),
                 image=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.image = pygame.image.load(image).convert_alpha() if image else None

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        if self.image:
            screen.blit(self.image, self.rect)
            if hovered:
                # optional: simple highlight overlay
                overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 50))
                screen.blit(overlay, self.rect)
        else:
            current_color = self.hover_color if hovered else self.color
            pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

def draw_slot(screen, x, y, w, h, font, content=None, highlight=False):
    """Draw a slot rectangle and the ingredient name if present."""
    rect = pygame.Rect(x, y, w, h)
    bg = (80, 80, 80) if not highlight else (120, 90, 20)
    pygame.draw.rect(screen, bg, rect, border_radius=6)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=6)
    if content:
        txt = font.render(content, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=rect.center)
        screen.blit(txt, txt_rect)
    else:
        placeholder = font.render("Empty", True, (180, 180, 180))
        screen.blit(placeholder, (x + 8, y + h//2 - placeholder.get_height()//2))
    return rect
