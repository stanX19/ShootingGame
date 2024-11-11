from __future__ import annotations
import math
import pygame
from srcs.constants import *
from srcs.classes.weapons import WeaponType
from srcs.classes.bullet import Bullet


class WaterParticle(Bullet):
    def __init__(self, x: float, y: float, angle, speed=3, rad=3,
                hp=1, dmg=0, lifespan=60 * 4, weapon=None):
        super().__init__(None, x, y, angle, speed, rad, hp=hp, dmg=dmg,
                         lifespan=lifespan,weapon=weapon)
        self.collide_rad: float = rad / 5
        self.mass: float = 10

    def move(self):
        super().move()
        self.dmg = self.speed / MAX_PARTICLE_COUNT * 25

    def distance_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)
