from __future__ import annotations
import math
import copy
import random
from typing import Any
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.bullet import Bullet
from srcs.constants import *

def is_tuple_of_two_numbers(val):
    return isinstance(val, tuple) and len(val) == 2 and all(isinstance(i, (int, float)) for i in val)

class BulletKwargsHandler:
    def __init__(self, bullet_kwargs: dict[str, Any]):
        self._original_kwargs: dict[str, Any] = bullet_kwargs
        self._static_kwargs: dict[str, Any] = {}
        self._random_kwargs: dict[str, Any] = {}

    def _set_static_and_random_kwargs(self):
        self._static_kwargs = {k: v for k, v in self._original_kwargs.items() if not is_tuple_of_two_numbers(v)}
        self._random_kwargs = {k: v for k, v in self._original_kwargs.items() if is_tuple_of_two_numbers(v)}

    def _get_generated_random_kwargs(self) -> dict[str, int | float]:
        return {key: random.uniform(*val) for key, val in self._random_kwargs.items()}

    def get_processed_kwargs(self) -> dict[str, Any]:
        return {**self._static_kwargs, **self._get_generated_random_kwargs()}

    def get_raw_kwargs(self):
        return self._original_kwargs.copy()

    def update_kwargs(self, new_items: dict[str, Any]):
        self._original_kwargs.update(new_items)
        self._set_static_and_random_kwargs()



class BulletSpawner:
    def __init__(self,
                 bullet_kwargs: BulletKwargsHandler,
                 bullet_class: type[Bullet] = Bullet,
                 spread: float = math.pi * 0.8,
                 spawn_radius: float = PLAYER_RADIUS * 5,
                 offset_factor: float = 1.0):
        self.bullet_kwargs: BulletKwargsHandler = bullet_kwargs
        self.bullet_class: type[Bullet] = bullet_class
        self.spread: float = spread
        self.spawn_radius: float = spawn_radius
        self.offset_factor: float = offset_factor

    def spawn_bullet(self, x, y, angle, parent: BaseUnit):
        bullet = self.bullet_class(
            parent.faction,
            x,
            y,
            angle,
            **self.bullet_kwargs.get_processed_kwargs(),
            parent=parent
        )
        return bullet

    def circular_spawn(self, x, y, angle: float, count: int, parent: BaseUnit) -> list[Bullet]:
        angle_offset = self.spread / count
        spawned_bullets = []

        for i in range(count):
            offset = (i - (count - 1) / 2) * angle_offset
            shoot_angle = angle + offset
            bullet_angle = angle + offset * self.offset_factor
            dy, dx = math.sin(shoot_angle) * self.spawn_radius, math.cos(shoot_angle) * self.spawn_radius
            dy, dx = dy - math.sin(angle) * self.spawn_radius, dx - math.cos(angle) * self.spawn_radius

            spawned_bullets.append(
                self.spawn_bullet(x + dx, y + dy, bullet_angle, parent)
            )

        return spawned_bullets