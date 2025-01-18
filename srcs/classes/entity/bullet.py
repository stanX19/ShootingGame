from __future__ import annotations
import random

from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.faction_data import FactionData
from srcs.constants import *
from srcs.classes.weapons import WeaponType


def _safe_value(value, default, reject=None):
    return value if value != reject else default


# Bullet class
class Bullet(FactionParticle):
    def __init__(self, faction: FactionData, x, y, angle, speed=None, rad=None,
                 color=None, hp=1.0, dmg=1.0, lifespan=None, weapon=None, **kwargs):
        if isinstance(weapon, WeaponType):
            speed = _safe_value(speed, weapon.speed)
            rad = _safe_value(rad, weapon.rad)
            hp = _safe_value(hp, weapon.hp, 1.0)
            dmg = _safe_value(dmg, weapon.dmg, 1.0)
            color = _safe_value(color, weapon.color)
            lifespan = _safe_value(lifespan, weapon.lifespan)
        speed = _safe_value(speed, 0.0)
        rad = _safe_value(rad, BULLET_RADIUS)
        color = _safe_value(color, BULLET_COLOR)
        lifespan = _safe_value(lifespan, 60 * 4)
        super().__init__(faction, x, y, angle, speed, rad, color, hp, dmg, **kwargs)
        if isinstance(lifespan, tuple) and len(lifespan) > 1:
            self.lifespan = random.randint(lifespan[0], lifespan[1])
        else:
            self.lifespan = lifespan

    def move(self):
        super().move()
        self.lifespan -= 1

    def is_dead(self):
        return super().is_dead() or self.x < 0 or self.x > MAP_WIDTH or\
            self.y < 0 or self.y > MAP_HEIGHT or self.lifespan <= 0