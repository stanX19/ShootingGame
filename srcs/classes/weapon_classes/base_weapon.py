from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.faction_data import FactionData


class BaseWeapon:
    def __init__(self, name: str, max_level:int=1):
        self.name: str = name
        self.level: int = 1
        self.max_level: int = max_level

    def fire(self, unit: BaseUnit, target_x: float, target_y: float):
        raise NotImplementedError("fire() must be implemented in derived classes.")
