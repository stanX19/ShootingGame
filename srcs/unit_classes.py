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
        super().__init__(faction, x, y, angle,
                         hp=10, dmg=1, score=100, speed=UNIT_SPEED * 3,
                         weapons=MainWeaponEnum.lazer_mini,
                         **kwargs)


class EliteUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=50, dmg=1, score=500, speed=UNIT_SPEED * 1.5,
                         shield_hp=100, shield_rad=100,
                         weapons=MainWeaponEnum.lazer_mini,
                         sub_weapons=MainWeaponEnum.missile,
                         **kwargs)


class SuperShootingUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=100, dmg=5, radius=40, score=2000, speed=UNIT_SPEED,
                         weapons=MainWeaponEnum.lazer,
                         **kwargs)


class RammerUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=125, radius=20, score=5000, speed=UNIT_SPEED,
                         variable_shape=True, variable_color=True,
                         weapons=MainWeaponEnum.booster_left,
                         sub_weapons=MainWeaponEnum.booster_right,
                         shoot_range=UNIT_SHOOT_RANGE * 5,
                         **kwargs)


class SniperUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=10, radius=50, score=10000, speed=UNIT_SPEED / 2,
                         shield_rad=100, shield_hp=500,
                         weapons=MainWeaponEnum.lazer_super,
                         # sub_weapons=MainWeaponEnum.lazer_mini,
                         shoot_range=UNIT_SHOOT_RANGE,
                         **kwargs)


class MiniMothershipUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        spawner = MainWeaponEnum.spawner.copy()
        spawner.change_bullet_class(BasicShootingUnit)
        spawner.update_bullet(controller=AIDroneController())

        super().__init__(faction, x, y, angle,
                         hp=250, dmg=10, radius=100, score=30000, speed=UNIT_SPEED / 2,
                         shield_rad=200, shield_hp=500,
                         weapons=MainWeaponEnum.lazer_super,
                         sub_weapons=spawner,
                         shoot_range=UNIT_SHOOT_RANGE,
                         **kwargs)


# TODO:
#  encapsulate main spawner weapon in a weapon class
#  such that player can use it too
class UnitMothership(Unit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        self.unit_dict = {
            Unit: 20,
            BasicShootingUnit: 20,
            EliteUnit: 3,
            RammerUnit: 3,
            MiniMothershipUnit: 1,
            SuperShootingUnit: 1
        }
        spawner = RandomSpawnerWeapon("mothership spawner", reload=SPAWN_CD * 1000)
        spawner.change_bullet_class(BasicShootingUnit)

        emergency = CompositeWeapon("Emergency", [
            SpawnerWeapon("1", reload=60 * 1000, min_count=12, bullet_class=BasicShootingUnit),
            SpawnerWeapon("1", reload=60 * 1000, min_count=12, bullet_class=BasicShootingUnit, angle_offset=math.pi/12)
        ] * 3, 400)

        super().__init__(faction, x, y,
                         hp=2000, dmg=125, speed=0,
                         variable_shape=True, variable_color=True,
                         radius=200, score=50000,
                         shield_hp=500, shield_rad=300,
                         controller=SmartAIController(),
                         weapons=emergency,
                         sub_weapons=spawner,
                         shoot_range=1500,
                         regen_rate=1/60/FPS*2000,  # recover in 60 seconds
                         **kwargs)

    def move(self):
        self.controller.fire_sub = True
        self.controller.fire_main = self.hp < self.max_hp / 2
        items = list(self.unit_dict.items())
        # random.shuffle(items)
        for unit_type, cap in items:
            count = len([i for i in self.faction.parent_list if isinstance(i, unit_type)])
            if count >= cap:
                continue
            self.sub_weapon.weapon.change_bullet_class(unit_type)
            self.controller.fire_sub = True
            break
        super().move()
