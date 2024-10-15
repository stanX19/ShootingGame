from __future__ import annotations
import math
import random

import pygame
from srcs.constants import *
from srcs.classes.weapons import WeaponType
from srcs.classes.game_particle import GameParticle
from srcs.classes.game_data import GameData


def _safe_value(value, default, reject=None):
    return value if value != reject else default


# Bullet class
class Bullet(GameParticle):
    def __init__(self, game_data: GameData, x, y, angle, speed=None, rad=None,
                 color=None, hp=1.0, dmg=1.0, lifespan=None, weapon=None):
        self.game_data: GameData = game_data

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
        super().__init__(x, y, angle, speed, rad, color, hp, dmg)
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