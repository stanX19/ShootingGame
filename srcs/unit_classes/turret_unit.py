from srcs.classes.controller import BotController
from srcs.classes.entity.unit import *

class _TurretUnit(Unit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 speed: float = 0.0,
                 controller: BaseController = SmartAIController(), **kwargs):
        super().__init__(faction, x, y, angle, speed=speed,
                         controller=controller, **kwargs)

    def move(self):
        super().move()

class ResourceUnit(_TurretUnit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 **kwargs):
        self._resource_size = 10000
        super().__init__(faction, x, y, angle, hp=self._resource_size,
                         radius=self._resource_size // 50, score=500, **kwargs)

    def move(self):
        super().move()
        self.add_score(1 / FPS)

class BulletTurretUnit(_TurretUnit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 **kwargs):
        super().__init__(faction, x, y, angle, weapons=MainWeaponEnum.machine_gun,
                         hp=10, radius=20, score=100, **kwargs)

class LazerTurretUnit(_TurretUnit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=30, dmg=5, radius=30, score=300,
                         weapons=MainWeaponEnum.lazer_mini,
                         shoot_range=UNIT_SHOOT_RANGE * 2,
                         **kwargs)

class AdvancedLazerTurretUnit(_TurretUnit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=100, dmg=5, radius=60, score=500,
                         weapons=MainWeaponEnum.lazer,
                         shoot_range=UNIT_SHOOT_RANGE * 3,
                         **kwargs)

class ShieldTurretUnit(_TurretUnit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: BaseController = AIController(), **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=10, dmg=5, radius=40, score=500,
                         shield_hp=500, shield_rad=300,
                         controller=controller,
                         **kwargs)

class MissileTurretUnit(_TurretUnit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=30, dmg=5, radius=30, score=500,
                         weapons=MainWeaponEnum.swarm,
                         shoot_range=UNIT_SHOOT_RANGE * 2,
                         **kwargs)