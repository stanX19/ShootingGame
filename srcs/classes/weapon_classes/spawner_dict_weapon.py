import random
from typing import override

from srcs.classes.controller import SmartAIController, BaseController, AIController
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.random_spawner_weapon import RandomSpawnerWeapon


class SpawnerDictWeapon(RandomSpawnerWeapon):
    def __init__(self, name: str, unit_dict: dict[type[BaseUnit], int]=None,
                 *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.unit_dict: dict[type[BaseUnit], int] = unit_dict if unit_dict is not None else {}
        # directly editing unit_dict will work

    @override
    def _shoot(self, unit: BaseUnit, target_x: float, target_y: float, **kwargs) -> list[GameParticle]:
        items = list(self.unit_dict.items())
        # items.reverse()
        random.shuffle(items)
        for unit_type, cap in items:
            count = len([i for i in unit.faction.parent_list if isinstance(i, unit_type)])
            if count >= cap:
                continue
            sample = unit_type(unit.faction, -100000, -100000)
            sample.kill()
            if sample.base_score > unit.score:
                continue
            self.change_bullet_class(unit_type)
            return super()._shoot(unit, target_x, target_y)
        return []