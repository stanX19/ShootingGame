import math

from srcs.classes.controller import AIDroneController, SmartAIController, BaseController, BotController
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.entity.unit import Unit
from srcs.classes.faction_data import FactionData
from srcs.classes.weapon_classes.composite_weapon import CompositeWeapon
from srcs.classes.weapon_classes.random_spawner_weapon import RandomSpawnerWeapon
from srcs.classes.weapon_classes.spawner_dict_weapon import SpawnerDictWeapon
from srcs.classes.weapon_classes.spawner_weapon import SpawnerWeapon
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum
from srcs.constants import UNIT_SHOOT_RANGE, UNIT_SPEED, SPAWN_CD, FPS, UNIT_SCORE
from srcs.unit_classes.advanced_weapons import AdvancedWeaponsEnum
from srcs.unit_classes.basic_unit import BasicLazerUnit, EliteUnit, RammerUnit, SuperShootingUnit, BasicShootingUnit


class SpawningTurretUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):

        super().__init__(faction, x, y, angle,
                         hp=50, dmg=5, radius=30, score=500, speed=0,
                         shield_rad=0, shield_hp=0,
                         sub_weapons=AdvancedWeaponsEnum.basic_spawner,
                         controller=BotController(),
                         **kwargs)
        self.score = 0

    def move(self):
        super().move()
        self.score += 100 / FPS / SPAWN_CD

class MiniMothershipUnit(Unit):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, **kwargs):
        super().__init__(faction, x, y, angle,
                         hp=250, dmg=10, radius=100, score=3000, speed=UNIT_SPEED / 2,
                         shield_rad=200, shield_hp=500,
                         weapons=MainWeaponEnum.charged_lazer,
                         sub_weapons=AdvancedWeaponsEnum.mini_spawner,
                         shoot_range=UNIT_SHOOT_RANGE,
                         controller=SmartAIController(),
                         **kwargs)
        self.score = 0


    def move(self):
        super().move()
        self.score += 100 / FPS / SPAWN_CD


class UnitMothership(Unit):
    def __init__(self, faction: FactionData, x: float, y: float, **kwargs):
        self.unit_dict = {
            Unit: 200,
            BasicShootingUnit: 10,
            BasicLazerUnit: 10,
            EliteUnit: 3,
            SuperShootingUnit: 2,
            MiniMothershipUnit: 1,
            RammerUnit: 3,
        }
        spawner = SpawnerDictWeapon("mothership spawner", reload=SPAWN_CD * 1000)

        emergency = CompositeWeapon("Emergency", [
            SpawnerWeapon("1", reload=60 * 1000, min_count=12, bullet_class=BasicLazerUnit),
            SpawnerWeapon("1", reload=60 * 1000, min_count=12, bullet_class=Unit, angle_offset=math.pi/12)
        ] * 3, 400)

        super().__init__(faction, x, y,
                         hp=20000, dmg=125, speed=0,
                         variable_shape=True, variable_color=True,
                         radius=200, score=5000,
                         shield_hp=500, shield_rad=300,
                         controller=SmartAIController(),
                         weapons=emergency,
                         sub_weapons=spawner,
                         shoot_range=1500,
                         regen_rate=1/60/FPS*2000,  # recover in 60 seconds
                         **kwargs)
        self.score = UNIT_SCORE

    def move(self):
        if isinstance(self.sub_weapon.weapon, SpawnerDictWeapon):
            self.sub_weapon.weapon.unit_dict = self.unit_dict
        self.controller.fire_sub = True
        self.controller.fire_main = self.hp < self.max_hp / 2
        self.score += UNIT_SCORE / FPS / SPAWN_CD / 2
        if self.hp < self.max_hp / 4:
            self.sub_weapon.overdrive_start()
            self.main_weapon.overdrive_start()
        super().move()

