from srcs.classes.controller import AIDroneController, BotController, AIController
from srcs.classes.entity.unit import Unit
from srcs.classes.weapon_classes.base_weapon import BaseWeapon
from srcs.classes.weapon_classes.general_weapon import GeneralWeapon
from srcs.classes.weapon_classes.spawner_dict_weapon import SpawnerDictWeapon
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum
from srcs.constants import UNIT_RADIUS
from srcs.unit_classes.basic_unit import FastLazerUnit, RammerUnit, EliteUnit, BasicShootingUnit, BasicLazerUnit, \
    SuperShootingUnit, ActivatedRammerUnit


class AdvancedWeaponsEnum:
    basic_spawner = SpawnerWeapon("Basic Spawner", reload=1000, min_count=1, max_count=3,
                                  bullet_class=BasicShootingUnit, controller=AIController())

    mini_spawner = MainWeaponEnum.spawner.copy()
    mini_spawner.name = "Fast Shooter Spawner"
    mini_spawner.change_bullet_class(FastLazerUnit)
    mini_spawner.update_bullet(controller=AIDroneController())

    rammer_spawner = SpawnerWeapon("Rammer Spawner", reload=10000, min_count=1, max_count=8,
                                   spawn_radius=UNIT_RADIUS * 2, bullet_class=ActivatedRammerUnit,
                                   controller=AIDroneController())

    elite_spawner = SpawnerWeapon("Elite Spawner", reload=15000, min_count=1, max_count=8,
                                  spawn_radius=UNIT_RADIUS * 2, bullet_class=EliteUnit,
                                  controller=AIDroneController())

    dict_spawner = SpawnerDictWeapon("Mixed Spawner", {
        BasicLazerUnit: 10,
        EliteUnit: 3,
        SuperShootingUnit: 3,
        RammerUnit: 3,
    })

ALL_ADVANCED_WEAPON_LIST: list[BaseWeapon] = [w for w in vars(AdvancedWeaponsEnum).values() if isinstance(w, BaseWeapon)]
