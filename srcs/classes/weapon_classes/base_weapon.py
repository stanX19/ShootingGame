from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.weapon_classes.level_handler import LevelHandler
from srcs.constants import BULLET_SPEED


class BaseWeapon:
    def __init__(self, name: str, max_level: int = 1, min_count: int = 1,
                 max_count: int = 1, growth_factor: int = 1):
        self.name: str = name
        self.level: LevelHandler = LevelHandler(max_level, min_count, max_count, growth_factor)

        # used by other classes
        self.bullet_speed = BULLET_SPEED
        self.recoil = 0

    def fire(self, unit: BaseUnit, target_x: float, target_y: float):
        raise NotImplementedError("fire() must be implemented in derived classes.")
