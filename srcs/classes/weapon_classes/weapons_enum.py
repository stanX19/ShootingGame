from __future__ import annotations

import math

from srcs.classes.entity.explosive import Explosive
from srcs.classes.entity.lazer import Lazer
from srcs.classes.weapon_classes.base_weapon import BaseWeapon
from srcs.classes.weapon_classes.booster_weapon import BoosterWeapon
from srcs.classes.weapon_classes.charged_weapon import ChargedWeapon
from srcs.classes.weapon_classes.composite_weapon import CompositeWeapon
from srcs.classes.weapon_classes.general_weapon import GeneralWeapon
from srcs.classes.weapon_classes.missile_weapon import MissileWeapon
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon
from srcs.classes.weapon_classes.teleport_weapon import TeleportWeapon
from srcs.constants import *


class MainWeaponEnum:
    machine_gun = GeneralWeapon("machine gun", reload=200, speed=15, max_count=5, radius=3, growth_factor=2,
                                offset_factor=0.1, dmg=1, hp=1, recoil=0, spread=math.pi, spawn_radius=UNIT_RADIUS * 3)
    piercing_machine_gun = GeneralWeapon("piercing machine gun", reload=300, speed=25, radius=5,
                                         growth_factor=2,  min_count=1, max_count=5,
                                         spread=math.pi, spawn_radius=UNIT_RADIUS * 3, offset_factor=0.1,
                                         dmg=5, hp=10, recoil=3)
    beam = GeneralWeapon("beam", reload=0, speed=1, radius=10, bullet_class=Lazer, lifespan=2, dmg=0.1,
                         hp=200)
    beam.get_speed = lambda unit: unit.distance_with(unit.target)

    lazer_mini = CompositeWeapon("Mini Lazer", [
        GeneralWeapon("lazer mini", reload=200, speed=50, radius=2, bullet_class=Lazer, lifespan=120, dmg=0.25,
                      hp=25, offset_factor=0.0, spawn_radius=UNIT_RADIUS, spread=math.pi * 0.8, min_count=1),
        GeneralWeapon("lazer mini", reload=200, speed=50, radius=2, bullet_class=Lazer, lifespan=120, dmg=0.25,
                      hp=25, offset_factor=0.0, spawn_radius=UNIT_RADIUS, spread=math.pi * 0.8, min_count=0),
        GeneralWeapon("lazer mini", reload=200, speed=50, radius=2, bullet_class=Lazer, lifespan=120, dmg=0.25,
                      hp=25, offset_factor=0.0, spawn_radius=UNIT_RADIUS, spread=math.pi * 0.8, min_count=-1),
    ], 200 // 3)
    lazer = lazer_mini.copy()
    lazer.update_bullet(speed=100, hp=100, radius=2)
    lazer.name = "lazer"
    # lazer = GeneralWeapon("lazer", reload=200, speed=100, min_count=1, max_count=3, radius=2,
    #                       growth_factor=1, bullet_class=Lazer, lifespan=120, dmg=1, hp=100,
    #                       offset_factor=0.0, spawn_radius=UNIT_RADIUS, spread=math.pi * 0.8)
    giant_canon = GeneralWeapon("giant canon", reload=200, speed=25, max_count=5, radius=20, recoil=1, hp=10, dmg=15,
                          offset_factor=0.0)
    charged_lazer = ChargedWeapon("charged lazer", reload=2000, speed=200, max_count=1, radius=10,
                                  bullet_class=Lazer, lifespan=120, dmg=3.5, hp=200, charge_lifespan=10)
    deleter = ChargedWeapon("deleter", reload=5000, speed=400, max_count=1, radius=10,
                                  bullet_class=Lazer, lifespan=120, dmg=5, hp=2500, charge_lifespan=2 * FPS)
    # lazer_mini = machine_gun
    # lazer = machine_gun
    shotgun = GeneralWeapon("shotgun", reload=600, speed=(25, 75), radius=3,
                            recoil=5, dmg=5, spread=math.pi * 0.4, lifespan=(5, 20),
                            min_count=100, max_count=250, growth_factor=75)
    fireworks = GeneralWeapon("fireworks", reload=2000, speed=(1, 55), radius=(3, 6),
                            recoil=0, dmg=(5, 100), spread=math.pi * 2, lifespan=(30, 40),
                            min_count=100, max_count=250, growth_factor=50, spawn_radius=0,
                                bullet_class=Explosive)
    destroyer = GeneralWeapon("giant canon", reload=2000, speed=25, max_count=3, radius=100, recoil=1, hp=100, dmg=10,
                              offset_factor=0.0)
    simple_missile = MissileWeapon("missile", 2000, max_count=8, min_count=2, growth_factor=1, dmg=10, hp=1,
                                   radius=MISSILE_RADIUS, speed=MISSILE_SPEED, spread=math.pi * 2)
    missile = MissileWeapon("missile", 2000, max_count=8, min_count=2, growth_factor=3,
                      dmg=10, hp=1, offset_factor=1, spread=math.pi * 2)
    swarm = CompositeWeapon("Swarm", [
        MissileWeapon("s1", 9000, max_count=8, min_count=2, growth_factor=1,
                      dmg=10, hp=1, offset_factor=1, spread=math.pi),
        MissileWeapon("s1", 9000, max_count=8, min_count=2, growth_factor=1,
                      dmg=10, hp=1, offset_factor=1, spread=math.pi * 2),
        MissileWeapon("s1", 9000, max_count=8, min_count=2, growth_factor=1,
                      dmg=10, hp=1, offset_factor=1, spread=math.pi * 3),
    ] * 2, 100)
    spike = MissileWeapon("Spike", 200, max_count=4, min_count=1, growth_factor=1,
                          dmg=1, hp=1, offset_factor=1, spread=math.pi, radius=2,
                          color=(255, 255, 255), speed=MISSILE_SPEED*2)
    torpedo = MissileWeapon("torpedo", 4000, dmg=200, hp=50, radius=20, spread=math.pi*2,
                            speed=MISSILE_SPEED/2, explosion_rad=400, explosion_lifespan=10)

    spawner = CompositeWeapon("Spawner", [
        SpawnerWeapon("Spawner 1", reload=10000, min_count=1, max_count=8, spawn_radius=UNIT_RADIUS * 2),
        SpawnerWeapon("Spawner 1", reload=10000, min_count=1, max_count=8, spawn_radius=UNIT_RADIUS * 2, angle_offset=math.pi * 0.25),
    ] * 2, shoot_interval=200)
    # shield = GeneralWeapon("shield", reload=2500, speed=1, max_count=100, hp=25, radius=1,
    #                     dmg=2.5 / ENEMY_RADIUS * ENEMY_SPEED, spread=2 * math.pi,
    #                     min_count=30, growth_factor=5)
    # nova = GeneralWeapon("nova", reload=0, min_count=1, max_count=3, speed=1000,
    #                   bullet_class=NOVA_CLASS, growth_factor=0.2)
    # piercing_machine_gun = GeneralWeapon("piercing machine gun", reload=250, speed=25, max_count=5, radius=3,
    #                                   growth_factor=1, offset_factor=0.1, dmg=2, hp=5, recoil=3)
    dancer = BoosterWeapon("Dancer", reload=0, speed=(-5, 0), radius=2, dmg=0.1, hp=10,
                           spread=math.pi, recoil=-5, lifespan=(1, 3), min_count=4, max_count=7)
    flash = TeleportWeapon("Flash", reload=500, speed=1, radius=5, dmg=0.0, hp=100,
                           spread=math.pi * 2, lifespan=3,
                           recoil=-100, min_count=4, max_count=7)
    warp = TeleportWeapon("Warp", reload=5000, speed=1, radius=25, dmg=0.0, hp=100,
                          spread=math.pi * 2,lifespan=3,
                          recoil=-500, min_count=5, max_count=8)


class SubWeaponEnum:
    sub_missile = MissileWeapon("sub missile", 2000, MISSILE_SPEED, 8, min_count=2,
                                dmg=MainWeaponEnum.swarm._bullet_kwargs.getattr('dmg'),
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


ALL_MAIN_WEAPON_LIST: list[BaseWeapon] = [w for w in vars(MainWeaponEnum).values() if isinstance(w, BaseWeapon)]
ALL_SUB_WEAPON_LIST: list[BaseWeapon] = [w for w in vars(SubWeaponEnum).values() if isinstance(w, BaseWeapon)]
#
# if __name__ == '__main__':
#     print(f"{' ':20}{'min dmg':>20}{'max dmg':>20}{'max lvl':>20}")
#     for w in ALL_MAIN_WEAPON_LIST:
#         print(f"{w.name:20}{w.get_min_dmg_constant():20.2f}{w.get_max_dmg_constant():20.2f}{w.max_lvl:20}")
