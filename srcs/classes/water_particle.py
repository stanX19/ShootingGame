from __future__ import annotations
import math
from srcs.constants import *
from srcs.classes.entity.bullet import Bullet


class WaterParticle(Bullet):
    def __init__(self, x: float, y: float, angle, speed=3, radius=3,
                 hp=1, dmg=0, lifespan=60 * 4):
        super().__init__(None, x, y, angle, speed, radius, hp=hp, dmg=dmg,
                         lifespan=lifespan)
        self.collide_rad: float = radius / 5
        self.mass: float = 10

    def move(self):
        super().move()
        self.dmg = self.speed / MAX_PARTICLE_COUNT * 25

    def distance_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)
