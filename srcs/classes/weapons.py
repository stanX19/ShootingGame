from __future__ import annotations
import math
import random
from typing import Union

from srcs.constants import *


MISSILE_CLASS = "missile"
LAZER_CLASS = "lazer"
NOVA_CLASS = "nova"
BULLET_CLASS = "bullet"


class WeaponType:
    def __init__(self, name: str, reload: float, velocity: [float, tuple[float, float]] = BULLET_SPEED,
                 count=None, radius=BULLET_RADIUS,
                 recoil=0, hp=1.0, dmg=1.0, spread=math.pi * 0.8, bullet_class: str = BULLET_CLASS,
                 min_bullet_count=1, growth_factor=0, offset_factor=1.0, color=BULLET_COLOR):
        self.name: str = name
        self.shot_delay: float = reload
        self._speed: Union[float, tuple[float, float]] = velocity
        if count is None:
            count = int(reload * 0.01) + 1
        self.bullet_count: int = count
        self.rad: float = radius
        self.recoil: float = recoil
        self.hp: float = hp
        self.dmg: float = dmg
        self.spread: float = spread
        self.min_bullet_count: int = min_bullet_count
        self.growth_factor: float = growth_factor
        self.offset_factor: float = offset_factor
        self.bullet_class: str = bullet_class
        self.color: tuple[int] = color
        self.level: int = 100

    @property
    def speed(self) -> float:
        if isinstance(self._speed, tuple):
            return random.uniform(self._speed[0], self._speed[1])
        else:
            return self._speed

    def __str__(self):
        return self.name

    pass


class MainWeaponEnum:
    machine_gun = WeaponType("machine gun", reload=100, velocity=10, count=10, radius=2, growth_factor=1,
                             offset_factor=0.1)
    lazer = WeaponType("lazer", reload=200, velocity=100, min_bullet_count=50, count=100, radius=1,
                       growth_factor=5, bullet_class=LAZER_CLASS)
    shotgun = WeaponType("shotgun", reload=1000, velocity=(25, 50), count=300, radius=1,
                         recoil=PLAYER_SPEED, dmg=1, min_bullet_count=10, growth_factor=10, spread=math.pi * 0.4)
    bomb = WeaponType("destroyer", reload=800, velocity=5, count=1, radius=25, recoil=25, hp=10000, dmg=10)
    missile = WeaponType("missile", 500, count=8, growth_factor=1, dmg=10,
                         radius=MISSILE_RADIUS, velocity=MISSILE_SPEED, bullet_class=MISSILE_CLASS)
    shield = WeaponType("shield", reload=2500, velocity=1, count=100, hp=50000, radius=1,
                        dmg=2.5 / ENEMY_RADIUS * ENEMY_SPEED, spread=2 * math.pi,
                        min_bullet_count=30, growth_factor=5)
    nova = WeaponType("nova", reload=0, count=min(1, int(MAX_PARTICLE_COUNT / 100)), velocity=1000,
                      bullet_class=NOVA_CLASS)


class SubWeaponEnum:
    sub_missile = WeaponType("sub missile", 2000, MISSILE_SPEED, 8, min_bullet_count=2,
                             dmg=MainWeaponEnum.missile.dmg,
                             growth_factor=1, bullet_class=MISSILE_CLASS, radius=MISSILE_RADIUS)

    sub_shield = WeaponType("sub shield", reload=10000, velocity=1, count=100, hp=50000, radius=1,
                            dmg=2.5 / ENEMY_RADIUS * ENEMY_SPEED, spread=2 * math.pi,
                            min_bullet_count=30, growth_factor=5)
