from srcs.classes.controller import SmartAIController, BaseController
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.random_spawner_weapon import RandomSpawnerWeapon


class SpawnerDictWeapon(RandomSpawnerWeapon):
    def __init__(self, name: str, unit_dict: dict[type[BaseUnit], int]=None,
                 controller: BaseController=SmartAIController(), *args, **kwargs):
        super().__init__(name, *args, **kwargs, controller=controller)
        self.unit_dict: dict[type[BaseUnit], int] = unit_dict if unit_dict is not None else {}
        # directly editing unit_dict will work

    def fire(self, unit: BaseUnit, target_x: float, target_y: float, **kwargs) -> list[GameParticle]:
        items = list(self.unit_dict.items())
        # random.shuffle(items)
        for unit_type, cap in items:
            count = len([i for i in unit.faction.parent_list if isinstance(i, unit_type)])
            if count >= cap:
                continue
            self.change_bullet_class(unit_type)
            return super().fire(unit, target_x, target_y)
        return []