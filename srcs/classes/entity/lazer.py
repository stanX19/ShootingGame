# Lazer class
import math

import pygame

from srcs.classes import algo
from srcs.classes.entity.bullet import Bullet
from srcs.classes.faction_data import FactionData
from srcs.classes.game_data import GameData
from srcs.classes.entity.game_particle import GameParticle
from srcs.constants import BULLET_SPEED, BULLET_RADIUS, BULLET_COLOR


class Lazer(Bullet):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, speed=BULLET_SPEED, radius=BULLET_RADIUS,
                 color=BULLET_COLOR, hp=10.0, dmg=1.0, lifespan=float('inf'),
                 **kwargs):
        super().__init__(faction, x, y, angle, speed, radius,
                         color, hp, dmg, lifespan, **kwargs)
        self._length = 0
        self.end_x = self.x
        self.end_y = self.y
        self.update_length()

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, val):
        self.hp = val / self.rad
        self.max_hp = val / self.rad
        self.update_length()

    def get_collision_rad(self):
        return self._length

    def update_length(self):
        self._length = (self.hp - 1) * self.rad
        angle = self.angle
        self.end_x = self.x + self._length * math.cos(angle)
        self.end_y = self.y + self._length * math.sin(angle)

    def draw(self, surface: pygame.Surface):
        """Draw the lazer as a line extending in its direction."""
        self.update_length()
        pygame.draw.line(surface, self.color,
                         (int(self.x), int(self.y)),
                         (int(self.end_x), int(self.end_y)),
                         int(self.rad) * 2 - 1)
        pygame.draw.circle(surface, self.color, (self.x, self.y), radius=self.rad - 3)
        pygame.draw.circle(surface, self.color, (self.end_x, self.end_y), radius=self.rad - 3)

    def angle_with_cord(self, x, y):
        nx, ny = algo.line_point_closest_point_on_line(self.prev_x, self.prev_y, self.end_x, self.end_y, x, y)
        return math.atan2(y - ny, x - nx)

    def move(self):
        super().move()
        self.update_length()

    def is_dead(self):
        """Check if the lazer is out of bounds, has no HP, or has expired."""
        return super().is_dead()
