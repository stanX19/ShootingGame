from __future__ import annotations
import math
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.bullet_kwargs_handler import BulletKwargsHandler
from srcs.constants import *


class BulletSpawner:
    def __init__(self,
                 bullet_kwargs: BulletKwargsHandler,
                 bullet_class: type[Bullet] = Bullet,
                 spread: float = math.pi * 0.8,
                 spawn_radius: float = 0,
                 offset_factor: float = 1.0,
                 angle_offset: float = 0.0):
        self.bullet_kwargs: BulletKwargsHandler = bullet_kwargs
        self.bullet_class: type[Bullet] = bullet_class
        self.spread: float = spread
        self.spawn_radius: float = spawn_radius
        self.offset_factor: float = offset_factor
        self.angle_offset: float = angle_offset

    def get_sample(self):
        return self.bullet_class(None, 0, 0, 0,
                                 **self.bullet_kwargs.get_processed_kwargs())

    def spawn_bullet(self, x, y, angle, parent: BaseUnit) -> GameParticle:
        bullet = self.bullet_class(
            parent.faction,
            **self.bullet_kwargs.get_processed_kwargs(),
            parent=parent
        )
        bullet.x = x
        bullet.y = y
        bullet.angle = angle
        return bullet

    def circular_spawn(self, x, y, angle: float, count: int, parent: BaseUnit) -> list:
        if count == 0:
            return []
        angle_offset = self.spread / count
        spawned_bullets = []

        for i in range(count):
            offset = (i - (count - 1) / 2) * angle_offset
            shoot_angle = angle + offset + self.angle_offset
            bullet_angle = shoot_angle * self.offset_factor
            dy, dx = math.sin(shoot_angle) * self.spawn_radius, math.cos(shoot_angle) * self.spawn_radius

            spawned_bullets.append(
                self.spawn_bullet(x + dx, y + dy, bullet_angle, parent)
            )

        return spawned_bullets