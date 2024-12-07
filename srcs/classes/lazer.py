# Lazer class
import math

import pygame

from srcs.classes.bullet import Bullet
from srcs.classes.game_data import GameData


class Lazer(Bullet):
    def __init__(self, game_data: GameData, x, y, angle, speed=None, rad=None, color=None, hp=1.0, dmg=1.0, lifespan=None, weapon=None):
        super().__init__(game_data, x, y, angle, speed, rad, color, hp, dmg, lifespan, weapon)
        self.length = 0
        self.end_x = self.x
        self.end_y = self.y
        self.actual_rad = self.rad
        self.update_length()

    def update_length(self):
        self.length = (self.hp - 1) * self.actual_rad
        angle = self.angle
        self.end_x = self.x + self.length * math.cos(angle)
        self.end_y = self.y + self.length * math.sin(angle)
        self.rad = self.length

    def draw(self, surface: pygame.Surface):
        """Draw the lazer as a line extending in its direction."""
        self.update_length()
        pygame.draw.line(surface, self.color,
                         (int(self.x), int(self.y)),
                         (int(self.end_x), int(self.end_y)),
                         int(self.actual_rad))

    def move(self):
        super().move()
        self.update_length()

    def is_dead(self):
        """Check if the lazer is out of bounds, has no HP, or has expired."""
        return super().is_dead()
