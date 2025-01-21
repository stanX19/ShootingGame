# Lazer class
import math

import pygame

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
                         int(self.actual_rad) * 2 - 1)
        pygame.draw.circle(surface, self.color, (self.x, self.y), radius=self.actual_rad - 3)
        pygame.draw.circle(surface, self.color, (self.end_x, self.end_y), radius=self.actual_rad - 3)

    def move(self):
        super().move()
        self.update_length()

    def is_dead(self):
        """Check if the lazer is out of bounds, has no HP, or has expired."""
        return super().is_dead()
