import math

from numpy.ma.core import count

from srcs.classes.controller import SmartAIController, AIDroneController
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.lazer import Lazer
from srcs.classes.entity.unit import *
from srcs.classes.weapon_classes.composite_weapon import CompositeWeapon
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


class SuicideUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=125, radius=20, score=5000, speed=UNIT_SPEED,
                         variable_shape=True, variable_color=True,
                         weapons=MainWeaponEnum.dancer,
                         sub_weapons=SubWeaponEnum.sub_inverted_dancer,
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


class UnitMothership(Unit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        self.unit_dict = {
            BasicShootingUnit: 30,
            EliteUnit: 3,
            SuicideUnit: 3,
            MiniMothershipUnit: 1,
            SuperShootingUnit: 5
        }
        spawner = SpawnerWeapon("mothership spawner", reload=1000)
        spawner.change_bullet_class(BasicShootingUnit)

        emergency = CompositeWeapon("Emergency", [
            SpawnerWeapon("1", reload=60 * 1000, min_count=12, bullet_class=BasicShootingUnit),
            SpawnerWeapon("1", reload=60 * 1000, min_count=12, bullet_class=BasicShootingUnit, angle_offset=math.pi/12)
        ] * 3, 400)

        super().__init__(faction, x, y,
                         hp=2000, dmg=125, speed=0,
                         variable_shape=True, variable_color=True,
                         radius=500, score=50000,
                         shield_hp=500, shield_rad=700,
                         controller=SmartAIController(),
                         weapons=emergency,
                         sub_weapons=spawner,
                         shoot_range=1500,
                         regen_rate=1/60/FPS*2000,  # recover in 60 seconds
                         **kwargs)

    def _spawner_sub_preprocess(self):
        self.controller.fire_sub = False
        self.controller.fire_main = self.hp < self.max_hp / 2
        for unit_type, cap in self.unit_dict.items():
            count = len([i for i in self.faction.parent_list if isinstance(i, unit_type)])
            if count >= cap:
                continue
            self.sub_weapon.weapon.change_bullet_class(unit_type)
            self.controller.fire_sub = True
            break

    def move(self):
        self._spawner_sub_preprocess()
        super().move()
