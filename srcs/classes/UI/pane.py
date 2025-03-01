import pygame

from srcs.classes.UI.button import RoundedButton
from srcs.classes.UI.ui_element import UIElement


class Pane(UIElement):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, margin: int = 10, spacing: int = 10):
        super().__init__(x1, y1, x2, y2, margin, spacing)
        self.child_list: list[UIElement] = []

    def get_all_child(self, class_type: type[object] = object):
        ret = []
        for child in self.child_list:
            if isinstance(child, class_type):
                ret.append(child)
            if isinstance(child, Pane):
                ret += child.get_all_child(class_type)
        return ret

    def set_child(self, *children: list[UIElement]):
        self.child_list = children
        self._arrange_child()

    def add_child(self, *children):
        self.child_list.extend(children)
        self._arrange_child()

    def _arrange_child(self):
        n = len(self.child_list)
        if not n:
            return
        width = (self.width - 2 * self.margin - (n - 1) * self.spacing) / n
        height = self.height - 2 * self.margin
        current_x = self.x + self.margin
        for child in self.child_list:
            x_padding = height // 2 if isinstance(child, RoundedButton) else 0
            child.x = current_x + x_padding
            child.y = self.top + self.margin
            child.width = width - 2 * x_padding
            child.height = height
            current_x += self.spacing + width

    def _draw(self, surface):
        # pygame.draw.rect(surface, (79,69,87), self)
        for child in self.child_list:
            child.draw(surface)

    def _handle_click_on_self(self):
        for child in self.child_list:
            child.handle_click()


class VPane(Pane):
    def _arrange_child(self):
        n = len(self.child_list)
        if not n:
            return
        width = self.width - 2 * self.margin
        height = (self.height - 2 * self.margin - (n - 1) * self.spacing) / n
        current_y = self.y + self.margin
        for child in self.child_list:
            x_padding = height // 2 if isinstance(child, RoundedButton) else 0
            child.x = self.x + self.margin + x_padding
            child.y = current_y
            child.width = width - 2 * x_padding
            child.height = height
            current_y += self.spacing + height