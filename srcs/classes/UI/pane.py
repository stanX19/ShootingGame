import pygame

from srcs.classes.UI.ui_element import UIElement
from srcs.classes.game_data import GameData


class Pane(UIElement):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, game_data: GameData, margin: int = 10, spacing: int = 5):
        super().__init__(game_data)
        self.x1: int = x1
        self.y1: int = y1
        self.x2: int = x2
        self.y2: int = y2
        self.margin: int = margin
        self.spacing: int = spacing
        self.buttons = []

    def set_buttons(self, *buttons):
        self.buttons = buttons
        self._arrange_buttons()

    def add_buttons(self, *buttons):
        self.buttons.extend(buttons)
        self._arrange_buttons()

    def _arrange_buttons(self):
        current_y = self.y1 + self.margin
        for button in self.buttons:
            button.x1 = self.x1 + self.margin
            button.y1 = current_y
            button.x2 = self.x2 - self.margin
            button.y2 = button.y1 + 40  # Assuming a fixed height of 40 for simplicity
            current_y = button.y2 + self.spacing

    def _draw(self, surface):
        pygame.draw.rect(surface, (0, 255, 0), (self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1))
        for button in self.buttons:
            button.draw(surface)

    def update(self):
        for button in self.buttons:
            button.update()