from srcs.classes.controller import BotController
from srcs.classes.entity.unit import *


class ResourceUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = BotController(), **kwargs):
        self._resource_size = 10000
        super().__init__(faction, x, y, angle, speed=0, hp=self._resource_size,
                         radius=self._resource_size // 50,
                         controller=controller, score=500, **kwargs)

    def move(self):
        super().move()
        self.add_score(1 / FPS)
        self.use_score(10)


class BasicShootingUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = SmartAIController(), **kwargs):
        super().__init__(faction, x, y, angle, weapons=MainWeaponEnum.machine_gun,
                         controller=controller, score=100, **kwargs)


class BasicLazerUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = SmartAIController(), **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=10, dmg=1, score=150, speed=UNIT_SPEED, radius=15,
                         weapons=MainWeaponEnum.lazer_mini,
                         controller=controller,
                         **kwargs)


class FastLazerUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = SmartAIController(), **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=3, dmg=1, score=50, speed=UNIT_SPEED * 5, radius=5,
                         weapons=MainWeaponEnum.lazer_mini,
                         controller=controller,
                         **kwargs)


class EliteUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = SmartAIController(), **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=50, dmg=1, score=500, speed=UNIT_SPEED * 1.5, radius=20,
                         shield_hp=100, shield_rad=100,
                         weapons=MainWeaponEnum.lazer_mini,
                         sub_weapons=MainWeaponEnum.swarm,
                         controller=controller,
                         **kwargs)


class SuperShootingUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = SmartAIController(), **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=100, dmg=5, radius=40, score=1000, speed=UNIT_SPEED,
                         weapons=MainWeaponEnum.lazer,
                         controller=controller,
                         **kwargs)


class RammerUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = AIController(), **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=50, radius=30, score=1500, speed=UNIT_SPEED * 2,
                         variable_shape=True, variable_color=True,
                         weapons=MainWeaponEnum.dancer,
                         shoot_range=UNIT_SHOOT_RANGE / 2,
                         controller=controller,
                         **kwargs)

class ActivatedRammerUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = AIController(), **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=50, radius=30, score=1500, speed=UNIT_SPEED,
                         variable_shape=True, variable_color=True,
                         weapons=MainWeaponEnum.dancer,
                         shoot_range=UNIT_SHOOT_RANGE,
                         controller=controller,
                         **kwargs)
    def move(self):
        self.controller.fire_main = True
        super().move()

class SniperUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = SmartAIController(), **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=10, radius=50, score=1000, speed=UNIT_SPEED / 2,
                         shield_rad=100, shield_hp=500,
                         weapons=MainWeaponEnum.charged_lazer,
                         # sub_weapons=MainWeaponEnum.lazer_mini,
                         shoot_range=UNIT_SHOOT_RANGE,
                         controller=controller,
                         **kwargs)
