from __future__ import annotations
import math
import pygame
from srcs.constants import *
from srcs.classes.weapons import WeaponType
from srcs.classes.game_particle import GameParticle


def _safe_value(value, default, reject=None):
    return value if value != reject else default


# Bullet class
class Bullet(GameParticle):
    def __init__(self, x, y, angle, speed=None, rad=None,
                 color=None, hp=1.0, dmg=1.0, lifespan=60 * 4, weapon=None):
        if isinstance(weapon, WeaponType):
            speed = _safe_value(speed, weapon.speed)
            rad = _safe_value(rad, weapon.rad)
            hp = _safe_value(hp, weapon.hp, 1.0)
            dmg = _safe_value(dmg, weapon.dmg, 1.0)
            color = _safe_value(color, weapon.color)
        speed = _safe_value(speed, 0.0)
        rad = _safe_value(rad, BULLET_RADIUS)
        color = _safe_value(color, BULLET_COLOR)
        super().__init__(x, y, angle, speed, rad, color, hp, dmg)
        self.lifespan = lifespan

    def move(self):
        super().move()
        self.lifespan -= 1

