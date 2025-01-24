from srcs.classes.controller import SmartAIController, AIDroneController
from srcs.classes.entity.unit import *
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
                         hp=20, dmg=1, score=500, speed=UNIT_SPEED * 1.5,
                         shield_hp=40, shield_rad=60,
                         weapons=MainWeaponEnum.lazer_mini,
                         sub_weapons=MainWeaponEnum.missile,
                         **kwargs)


class SuperShootingUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=100, dmg=5, radius=15, score=2000, speed=UNIT_SPEED,
                         weapons=MainWeaponEnum.lazer,
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

class SuicideUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=125, radius=20, speed=UNIT_SPEED,
                         variable_shape=True, variable_color=True,
                         weapons=MainWeaponEnum.dancer,
                         sub_weapons=SubWeaponEnum.sub_inverted_dancer,
                         shoot_range=UNIT_SHOOT_RANGE * 5,
                         **kwargs)


class UnitMiniMothership(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        spawner = MainWeaponEnum.spawner.copy()
        spawner.change_bullet_class(BasicShootingUnit)
        spawner.update_bullet(controller=AIDroneController())

        super().__init__(faction, x, y, angle,
                         hp=250, dmg=10, radius=100, score=10000, speed=UNIT_SPEED / 2,
                         shield_rad=200, shield_hp=500,
                         weapons=MainWeaponEnum.lazer_super,
                         sub_weapons=spawner,
                         shoot_range=UNIT_SHOOT_RANGE,
                         **kwargs)



class UnitMothership(Unit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        super().__init__(faction, x, y,
                         hp=1000, dmg=125, speed=0,
                         variable_shape=True, variable_color=True,
                         radius=100, score=10000,
                         shield_hp=500, shield_rad=200,
                         controller=SmartAIController(),
                         weapons=MainWeaponEnum.bomb,
                         shoot_range=1500,
                         # importance=1,
                         regen_rate=1/30/FPS*1000,
                         **kwargs)

