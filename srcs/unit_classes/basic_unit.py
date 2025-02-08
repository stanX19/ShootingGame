import math

import random

from srcs.classes.controller import SmartAIController, AIDroneController
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.lazer import Lazer
from srcs.classes.entity.unit import *
from srcs.classes.weapon_classes.composite_weapon import CompositeWeapon
from srcs.classes.weapon_classes.random_spawner_weapon import RandomSpawnerWeapon
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon
from srcs.classes.weapon_classes.weapons_enum import SubWeaponEnum


class BasicShootingUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle, weapons=MainWeaponEnum.machine_gun)


class BasicLazerUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=10, dmg=1, score=100, speed=UNIT_SPEED, radius=15,
                         weapons=MainWeaponEnum.lazer_mini,
                         **kwargs)


class FastLazerUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=1, dmg=1, score=100, speed=UNIT_SPEED * 10, radius=5,
                         weapons=MainWeaponEnum.lazer_mini,
                         **kwargs)


class EliteUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=50, dmg=1, score=400, speed=UNIT_SPEED * 1.5, radius=20,
                         shield_hp=100, shield_rad=100,
                         weapons=MainWeaponEnum.lazer_mini,
                         sub_weapons=MainWeaponEnum.swarm,
                         **kwargs)


class SuperShootingUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=100, dmg=5, radius=40, score=200, speed=UNIT_SPEED,
                         weapons=MainWeaponEnum.lazer,
                         **kwargs)


class RammerUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=125, radius=30, score=500, speed=UNIT_SPEED,
                         variable_shape=True, variable_color=True,
                         weapons=MainWeaponEnum.dancer,
                         shoot_range=UNIT_SHOOT_RANGE * 5,
                         **kwargs)


class SniperUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=10, radius=50, score=1000, speed=UNIT_SPEED / 2,
                         shield_rad=100, shield_hp=500,
                         weapons=MainWeaponEnum.lazer_super,
                         # sub_weapons=MainWeaponEnum.lazer_mini,
                         shoot_range=UNIT_SHOOT_RANGE,
                         **kwargs)
