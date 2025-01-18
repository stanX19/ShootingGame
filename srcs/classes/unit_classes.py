from srcs.classes.controller import SmartAIController
from srcs.classes.entity.unit import *


class BasicShootingUnit(ShootingUnit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        super().__init__(faction, x, y,
                         hp=10, dmg=1, score=100, speed=UNIT_SPEED * 5,
                         weapons=MainWeaponEnum.lazer_mini,
                         **kwargs)


class EliteUnit(ShootingUnit, ShieldedUnit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        super().__init__(faction, x, y,
                         hp=20, dmg=1, score=500, speed=UNIT_SPEED * 1.5,
                         weapons=MainWeaponEnum.lazer_mini,
                         sub_weapons=MainWeaponEnum.missile,
                         **kwargs)


class SuperShootingUnit(ShootingUnit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        super().__init__(faction, x, y,
                         hp=100, dmg=5, radius=15, score=2000, speed=UNIT_SPEED,
                         weapons=MainWeaponEnum.lazer,
                         **kwargs)


class SniperUnit(ShootingUnit, ShieldedUnit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        super().__init__(faction, x, y,
                         hp=250, dmg=10, radius=50, score=10000, speed=UNIT_SPEED / 2,
                         weapons=MainWeaponEnum.lazer_super,
                         # sub_weapons=MainWeaponEnum.lazer_mini,
                         shoot_range=UNIT_SHOOT_RANGE,
                         **kwargs)

class SuicideUnit(ShootingUnit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        super().__init__(faction, x, y,
                         hp=250, dmg=15, radius=20, speed=UNIT_SPEED,
                         variable_shape=True, variable_color=True,
                         weapons=MainWeaponEnum.dancer,
                         shoot_range=UNIT_SHOOT_RANGE,
                         **kwargs)


class UnitMiniMothership(ShootingUnit, ShieldedUnit, SpawningUnit):
    pass


class UnitMothership(ShieldedUnit, ShootingUnit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        super().__init__(faction, x, y,
                         hp=5000, dmg=1, speed=0,
                         variable_shape=True, variable_color=True,
                         radius=500, score=50000,
                         shield_hp=500, shield_rad=1000,
                         controller=SmartAIController(),
                         weapons=MainWeaponEnum.bomb,
                         shoot_range=1500,
                         **kwargs)
