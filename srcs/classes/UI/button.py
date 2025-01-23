from typing import Callable

import pygame

from srcs.classes.UI.ui_element import UIElement
from srcs.classes.game_data import GameData


class Button(UIElement):
    def __init__(self, text: str, on_click: Callable, game_data: GameData, x1: int = -1, y1: int = -1, x2: int = -1, y2: int = -1):
        super().__init__(game_data)
        self.text: str = text
        self.on_click: Callable = on_click
        self.x1: int = x1
        self.y1: int = y1
        self.x2: int = x2
        self.y2: int = y2

    def update(self):
        if self.is_clicked():
            self.on_click()

    def is_clicked(self):
        mx, my = self.game_data.get_mouse_pos()
        if self.game_data.left_mouse_down and self.x1 <= mx <= self.x2 and self.y1 <= my <= self.y2:
            return True
        return False

    def _draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), (self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1))
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surface, (self.x1, self.y1))