from __future__ import annotations
import random

from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.faction_data import FactionData
from srcs.constants import *


# Bullet class
class Bullet(FactionParticle):
    def __init__(self, faction: FactionData, x, y, angle, speed=BULLET_SPEED, radius=BULLET_RADIUS,
                 color=BULLET_COLOR, hp=1.0, dmg=1.0, lifespan=float('inf'), **kwargs):
        super().__init__(faction, x, y, angle, speed, radius, color, hp, dmg, **kwargs)
        assert not isinstance(lifespan, tuple)
        self.lifespan = lifespan

    def move(self):
        super().move()
        self.lifespan -= 1

    def is_dead(self):
        return super().is_dead() or self.x < 0 or self.x > MAP_WIDTH or\
            self.y < 0 or self.y > MAP_HEIGHT or self.lifespan <= 0