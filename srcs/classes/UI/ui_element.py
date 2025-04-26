import pygame

from srcs.classes.game_data import GameData


class UIElement(pygame.Rect):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, margin: int, spacing: int):
        super().__init__(x1, y1, x2 - x1, y2 - y1)
        self.margin: int = margin
        self.spacing: int = spacing
        self._active: bool = True

    def draw(self, surface):
        if self._active:
            self._draw(surface)

    def _draw(self, surface: pygame.Surface):
        raise NotImplementedError(f"_draw() not implemented in {self.__class__.__name__}")

    def is_hover(self):
        mx, my = pygame.mouse.get_pos()
        return self.left <= mx <= self.right and self.top <= my <= self.bottom

    def handle_click(self):
        if not self._active or not self.is_hover():
            return False
        self._handle_click_on_self()
        return True

    def _handle_click_on_self(self):
        raise NotImplementedError(f"_handle_click() not implemented in {self.__class__.__name__}")

    def is_active(self):
        return self._active

    def hide(self):
        self._active = False

    def show(self):
        self._active = True


