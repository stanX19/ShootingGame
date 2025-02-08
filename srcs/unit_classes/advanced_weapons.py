from srcs.classes.controller import AIDroneController
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum
from srcs.constants import UNIT_RADIUS
from srcs.unit_classes.basic_unit import FastLazerUnit, RammerUnit, EliteUnit


class AdvancedWeaponsEnum:
    mini_spawner = MainWeaponEnum.spawner.copy()
    mini_spawner.change_bullet_class(FastLazerUnit)
    mini_spawner.update_bullet(controller=AIDroneController())

    rammer_spawner = SpawnerWeapon("Rammer Spawner", reload=20000, min_count=1, max_count=8,
                                   spawn_radius=UNIT_RADIUS * 2, bullet_class=RammerUnit,
                                   controller=AIDroneController())

    elite_spawner = SpawnerWeapon("Elite Spawner", reload=30000, min_count=1, max_count=8,
                                  spawn_radius=UNIT_RADIUS * 2, bullet_class=EliteUnit,
                                  controller=AIDroneController())
