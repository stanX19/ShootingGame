import math

from srcs.classes.controller import AIDroneController, SmartAIController
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.unit import Unit
from srcs.classes.faction_data import FactionData
from srcs.classes.weapon_classes.composite_weapon import CompositeWeapon
from srcs.classes.weapon_classes.random_spawner_weapon import RandomSpawnerWeapon
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum
from srcs.constants import UNIT_SHOOT_RANGE, UNIT_SPEED, SPAWN_CD, FPS
from srcs.unit_classes.advanced_weapons import AdvancedWeaponsEnum
from srcs.unit_classes.basic_unit import BasicLazerUnit, EliteUnit, RammerUnit, SuperShootingUnit, BasicShootingUnit


class MiniMothershipUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=10, radius=100, score=3000, speed=UNIT_SPEED / 2,
                         shield_rad=200, shield_hp=500,
                         weapons=MainWeaponEnum.lazer_super,
                         sub_weapons=AdvancedWeaponsEnum.mini_spawner,
                         shoot_range=UNIT_SHOOT_RANGE,
                         **kwargs)


# TODO:
#  encapsulate main spawner weapon in a weapon class
#  such that player can use it too
class UnitMothership(Unit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        self.unit_dict = {
            Unit: 60,
            BasicShootingUnit: 30,
            BasicLazerUnit: 10,
            EliteUnit: 3,
            RammerUnit: 3,
            MiniMothershipUnit: 1,
            SuperShootingUnit: 2
        }
        spawner = RandomSpawnerWeapon("mothership spawner", reload=SPAWN_CD * 1000)
        spawner.change_bullet_class(BasicLazerUnit)

        emergency = CompositeWeapon("Emergency", [
            SpawnerWeapon("1", reload=60 * 1000, min_count=4, bullet_class=BasicLazerUnit),
            SpawnerWeapon("1", reload=60 * 1000, min_count=12, bullet_class=Unit, angle_offset=math.pi/12)
        ] * 3, 400)

        super().__init__(faction, x, y,
                         hp=2000, dmg=125, speed=0,
                         variable_shape=True, variable_color=True,
                         radius=200, score=5000,
                         shield_hp=500, shield_rad=300,
                         controller=SmartAIController(),
                         weapons=emergency,
                         sub_weapons=spawner,
                         shoot_range=1500,
                         regen_rate=1/60/FPS*2000,  # recover in 60 seconds
                         **kwargs)

    def move(self):
        self.controller.fire_sub = False
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
