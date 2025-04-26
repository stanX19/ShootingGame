import math
import random
from typing import override

from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon


class RandomSpawnerWeapon(SpawnerWeapon):
    @override
    def _shoot(self, unit: BaseUnit, target_x: float, target_y: float, **kwargs) -> list[GameParticle]:
        self._spawner.angle_offset = random.uniform(-math.pi, math.pi)
        return super()._shoot(unit, target_x, target_y)