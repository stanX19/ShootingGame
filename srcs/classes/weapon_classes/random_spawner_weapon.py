import math
import random

from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon


class RandomSpawnerWeapon(SpawnerWeapon):
    def fire(self, unit: BaseUnit, target_x: float, target_y: float, **kwargs) -> list[GameParticle]:
        self._spawner.angle_offset = random.uniform(-math.pi, math.pi)
        return super().fire(unit, target_x, target_y)