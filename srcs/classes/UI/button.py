from typing import Callable

import pygame

from srcs.classes.UI.ui_element import UIElement


class RoundedButton(UIElement):
    def __init__(self, text: str, on_click: Callable, x1: int = -1, y1: int = -1, x2: int = -1, y2: int = -1,
                 font_size: int = 28):
        super().__init__(x1, y1, x2, y2, 10, 0)
        self.color = (109, 93, 110)
        self.margin = 0
        self.text: str = text
        self.on_click: Callable = on_click
        self.font = pygame.font.Font(None, font_size)

    def _draw_text_wrapped(self, surface, text, font, color, rect):
        paragraphs = text.split('\n')
        lines = []
        max_width = rect.width

        for paragraph in paragraphs:
            words = paragraph.split(' ')
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                width, _ = font.size(test_line)
                if width <= max_width:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

        total_text_height = len(lines) * font.get_height()
        y_offset = rect.top + (rect.height - total_text_height) // 2  # Center vertically

        for line in lines:
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(
                topleft=(rect.left + self.margin, y_offset))  # Center horizontally
            surface.blit(text_surface, text_rect)
            y_offset += font.get_height()

    def _draw(self, surface):
        self.color = (109, 93, 110) if not self.is_hover() else (125, 133, 151)
        pygame.draw.rect(surface, self.color, self)
        pygame.draw.circle(surface, self.color, self.midleft, self.height // 2)
        pygame.draw.circle(surface, self.color, self.midright, self.height // 2)
        text_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self._draw_text_wrapped(surface, self.text, self.font, (0xF4, 0xEE, 0xE0), text_rect)

    def _handle_click_on_self(self):
        self.on_click()
