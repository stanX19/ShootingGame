from srcs.classes.controller import BotController
from srcs.classes.unit import *


class BasicShootingUnit(ShootingUnit):
    def __init__(self, game_data: GameData, x: float, y: float, targets: list[GameParticle],
                 parent_list: list[GameParticle], **kwargs):
        super().__init__(game_data, x, y, targets, parent_list,
                         hp=1, dmg=1, score=100, speed=UNIT_SPEED,
                         weapons=MainWeaponEnum.lazer_mini,
                         **kwargs)


class EliteUnit(ShootingUnit, ShieldedUnit):
    def __init__(self, game_data: GameData, x: float, y: float, targets: list[GameParticle],
                 parent_list: list[GameParticle], **kwargs):
        super().__init__(game_data, x, y, targets, parent_list,
                         hp=10, dmg=1, score=500, speed=UNIT_SPEED * 1.5,
                         weapons=MainWeaponEnum.lazer_mini,
                         **kwargs)


class SuperShootingUnit(ShootingUnit):
    def __init__(self, game_data: GameData, x: float, y: float, targets: list[GameParticle],
                 parent_list: list[GameParticle], **kwargs):
        super().__init__(game_data, x, y, targets, parent_list,
                         hp=30, dmg=5, radius=30, score=2000, speed=UNIT_SPEED,
                         weapons=MainWeaponEnum.lazer,
                         **kwargs)


class SniperUnit(ShootingUnit, ShieldedUnit):
    def __init__(self, game_data: GameData, x: float, y: float, targets: list[GameParticle],
                 parent_list: list[GameParticle], **kwargs):
        super().__init__(game_data, x, y, targets, parent_list,
                         hp=100, dmg=5, radius=100, score=10000, speed=UNIT_SPEED / 2,
                         weapons=MainWeaponEnum.lazer_super,
                         sub_weapons=MainWeaponEnum.missile,
                         shoot_range=UNIT_SHOOT_RANGE * 2,
                         **kwargs)


class UnitMiniMothership(ShootingUnit, ShieldedUnit, SpawningUnit):
    pass


class UnitMothership(ShieldedUnit):
    def __init__(self, game_data: GameData, x: float, y: float, targets: list[GameParticle],
                 parent_list: list[GameParticle], **kwargs):
        super().__init__(game_data, x, y, targets, parent_list,
                         hp=1000, dmg=50, variable_shape=True, variable_color=True,
                         radius=500, score=50000,
                         shield_hp=500, shield_rad=1000,
                         controller=BotController(),
                         **kwargs)
