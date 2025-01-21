from __future__ import annotations

import math

from srcs.classes.entity.explosive import Explosive
from srcs.classes.entity.lazer import Lazer
from srcs.classes.weapon_classes.booster_weapon import BoosterWeapon
from srcs.classes.weapon_classes.charged_weapon import ChargedWeapon
from srcs.classes.weapon_classes.composite_weapon import CompositeWeapon
from srcs.classes.weapon_classes.general_weapon import GeneralWeapon
from srcs.classes.weapon_classes.missile_weapon import MissileWeapon
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon
from srcs.constants import *


class MainWeaponEnum:
    machine_gun = GeneralWeapon("machine gun", reload=300, speed=15, max_count=1, radius=3, growth_factor=1,
                                offset_factor=0.1, dmg=1, hp=1, recoil=3)
    piercing_machine_gun = GeneralWeapon("piercing machine gun", reload=800, speed=25, max_count=1, radius=5,
                                         growth_factor=1,
                                         offset_factor=0.1, dmg=8, hp=1, recoil=3)
    lazer_mini = GeneralWeapon("lazer mini", reload=200, speed=50, min_count=1, max_count=1, radius=2,
                               growth_factor=5, bullet_class=Lazer, lifespan=120, dmg=1, hp=25, spread=math.pi / 8)
    lazer = GeneralWeapon("lazer", reload=200, speed=100, min_count=1, max_count=1, radius=2,
                          growth_factor=5, bullet_class=Lazer, lifespan=120, dmg=1, hp=100)
    giant_canon = GeneralWeapon("giant canon", reload=200, speed=50, max_count=1, radius=20, recoil=5, hp=10, dmg=10)
    lazer_super = ChargedWeapon("lazer super", reload=2000, speed=200, min_count=1, max_count=1, radius=10,
                                growth_factor=5, bullet_class=Lazer, lifespan=120, dmg=5, hp=200, charge_lifespan=10)
    # lazer_mini = machine_gun
    # lazer = machine_gun
    shotgun = GeneralWeapon("shotgun", reload=600, speed=(25, 50), max_count=300, radius=1,
                            recoil=PLAYER_SPEED, dmg=5, min_count=25, growth_factor=25, spread=math.pi * 0.4,
                            lifespan=(5, 20))
    bomb = GeneralWeapon("destroyer", reload=2000, speed=10, max_count=1, radius=50, recoil=5, hp=1, dmg=10,
                         bullet_class=Explosive)
    simple_missile = MissileWeapon("missile", 1000, max_count=8, min_count=2, growth_factor=1, dmg=10, hp=1,
                                   radius=MISSILE_RADIUS, speed=MISSILE_SPEED, spread=math.pi * 2)
    missile = CompositeWeapon("Swarm Missile", [
        MissileWeapon("missile", 3000, max_count=8, min_count=2, growth_factor=1,
                      dmg=10, hp=1, offset_factor=1, spread=math.pi),
        MissileWeapon("missile", 3000, max_count=8, min_count=2, growth_factor=1,
                      dmg=10, hp=1, offset_factor=1, spread=math.pi * 2),
        MissileWeapon("missile", 3000, max_count=8, min_count=2, growth_factor=1,
                      dmg=10, hp=1, offset_factor=1, spread=math.pi * 3),
    ], 100)

    spawner = CompositeWeapon("Spawner", [
        SpawnerWeapon("Spawner 1", reload=10000, min_count=4, spawn_radius=UNIT_RADIUS * 5),
    ] * 5, shoot_interval=200)
    # shield = GeneralWeapon("shield", reload=2500, speed=1, max_count=100, hp=25, radius=1,
    #                     dmg=2.5 / ENEMY_RADIUS * ENEMY_SPEED, spread=2 * math.pi,
    #                     min_count=30, growth_factor=5)
    # nova = GeneralWeapon("nova", reload=0, min_count=1, max_count=3, speed=1000,
    #                   bullet_class=NOVA_CLASS, growth_factor=0.2)
    # piercing_machine_gun = GeneralWeapon("piercing machine gun", reload=250, speed=25, max_count=5, radius=3,
    #                                   growth_factor=1, offset_factor=0.1, dmg=2, hp=5, recoil=3)
    dancer = BoosterWeapon("dancer", reload=0, speed=(-5, 0), radius=2, dmg=0.1, hp=10,
                           min_count=1, max_count=20, growth_factor=1, spread=math.pi,
                           recoil=-20, lifespan=(1, 3))


class SubWeaponEnum:
    sub_missile = MissileWeapon("sub missile", 2000, MISSILE_SPEED, 8, min_count=2,
                                dmg=MainWeaponEnum.missile._bullet_kwargs.getattr('dmg'),
                                growth_factor=1, radius=MISSILE_RADIUS)

    sub_shield = GeneralWeapon("sub shield", reload=7500, speed=1, max_count=100, hp=10, radius=1,
                               dmg=2.5 / UNIT_RADIUS * UNIT_SPEED, spread=2 * math.pi,
                               min_count=30, growth_factor=5)

    sub_dancer = BoosterWeapon("sub dancer", reload=0, speed=(-5, 0), radius=2, dmg=0.0, hp=1,
                               min_count=1, max_count=5, growth_factor=1, spread=math.pi,
                               recoil=-10, lifespan=(1, 60), bullet_class=Lazer)
    sub_inverted_dancer = BoosterWeapon("sub inverted dancer", reload=0, speed=(0, 5), radius=2, dmg=0.0, hp=1,
                                        min_count=1, max_count=5, growth_factor=1, spread=math.pi,
                                        recoil=10, lifespan=(1, 60), bullet_class=Lazer)


ALL_MAIN_WEAPON_LIST: list[GeneralWeapon] = [w for w in vars(MainWeaponEnum).values() if isinstance(w, GeneralWeapon)]
ALL_SUB_WEAPON_LIST: list[GeneralWeapon] = [w for w in vars(SubWeaponEnum).values() if isinstance(w, GeneralWeapon)]
#
# if __name__ == '__main__':
#     print(f"{' ':20}{'min dmg':>20}{'max dmg':>20}{'max lvl':>20}")
#     for w in ALL_MAIN_WEAPON_LIST:
#         print(f"{w.name:20}{w.get_min_dmg_constant():20.2f}{w.get_max_dmg_constant():20.2f}{w.max_lvl:20}")
