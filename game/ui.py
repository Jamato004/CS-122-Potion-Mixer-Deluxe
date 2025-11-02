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


def draw_wrapped_text(screen, text, x, y, max_width, font, color):
    """Draw text on multiple lines if it exceeds max_width."""
    words = text.split(' ')
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            surface = font.render(line, True, color)
            screen.blit(surface, (x, y))
            y += font.get_height() + 2
            line = word
    if line:
        surface = font.render(line, True, color)
        screen.blit(surface, (x, y))


class Popup:
    """Handles a station popup with ingredient slots, Mix, and Close buttons."""

    def __init__(self, screen, station_name, x, y, w, h, font, max_slots=3):
        self.screen = screen
        self.station_name = station_name
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.max_slots = max_slots
        self.slots = [None] * self.max_slots

        # Buttons
        self.mix_btn = Button("Mix", x + w - 110, y + h - 56, 90, 40, font)
        self.close_btn = Button("Close", x + w - 210, y + h - 56, 90, 40, font)

    def draw(self):
        pygame.draw.rect(self.screen, (18, 18, 30), self.rect, border_radius=8)
        pygame.draw.rect(self.screen, (180, 180, 180), self.rect, 2, border_radius=8)

        title = self.font.render(f"{self.station_name}", True, (255, 255, 255))
        self.screen.blit(title, (self.rect.x + 12, self.rect.y + 8))

        for i, slot_rect in enumerate(self.slot_rects()):
            draw_slot(self.screen, slot_rect.x, slot_rect.y, slot_rect.w, slot_rect.h,
                      self.font, content=self.slots[i])

        self.mix_btn.draw(self.screen)
        self.close_btn.draw(self.screen)

        # Hint text
        last_slot_bottom = self.slot_rects()[-1].bottom
        hint_y = last_slot_bottom + 8
        draw_wrapped_text(
            self.screen,
            "Select ingredient -> click slot to place",
            self.rect.x + 12,
            hint_y,
            self.rect.w - 24,
            self.font,
            (180, 180, 180)
        )

    def slot_rects(self):
        x = self.rect.x + 12
        y = self.rect.y + 40
        w = self.rect.w - 24
        h = 38
        gap = 10
        return [pygame.Rect(x, y + i * (h + gap), w, h) for i in range(self.max_slots)]
