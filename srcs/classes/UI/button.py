from typing import Callable

import pygame

from srcs.classes.UI.ui_element import UIElement
from srcs.classes.game_data import GameData


class Button(UIElement):
    def __init__(self, text: str, on_click: Callable, x1: int = -1, y1: int = -1, x2: int = -1, y2: int = -1):
        super().__init__(x1, y1, x2, y2, 10, 0)
        self.color = (109,93,110)
        self.text: str = text
        self.on_click: Callable = on_click
        self.font = pygame.font.Font(None, 36)

    def _draw(self, surface):
        self.color = (109,93,110) if not self.is_hover() else (125,133,151)
        pygame.draw.rect(surface, self.color, self)
        text_surface = self.font.render(self.text, True, (0xF4, 0xEE, 0xE0))
        text_rect = text_surface.get_rect(center=self.center)
        surface.blit(text_surface, text_rect)

    def _handle_click_on_self(self):
        self.on_click()