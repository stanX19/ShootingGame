import pygame

from srcs.classes.game_data import GameData


class UIElement:
    def __init__(self, game_data: GameData):
        self._active: bool = True
        self.game_data: GameData = game_data

    def draw(self, surface):
        if self._active:
            self._draw(surface)

    def _draw(self, surface: pygame.Surface):
        raise NotImplementedError(f"_draw() not implemented in {self.__class__.__name__}")

    def hide(self):
        self._active = False

    def show(self):
        self._active = True

    def update(self):
        pass


