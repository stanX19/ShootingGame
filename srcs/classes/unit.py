from __future__ import annotations
import pygame
import math
import random
from typing import Sequence, Optional

from srcs import utils
from srcs.classes.shield import Shield
from srcs.classes.base_unit import BaseUnit
from srcs.classes.weapon_handler import WeaponHandler
from srcs.classes.weapons import ALL_MAIN_WEAPON_LIST
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.bullet import Bullet
from srcs.classes.effect import Effect
from srcs.classes.game_data import GameData
from srcs.classes.draw_utils import draw_arrow
from srcs.classes import algo
from srcs.classes.controller import BaseController, AIController


class Unit(BaseUnit):
    def __init__(self, game_data: GameData, x: float, y: float,
                 targets: list[GameParticle], parent_list: list[GameParticle],
                 controller: Optional[BaseController] = None, **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, **kwargs)
        self.controller: BaseController = AIController() if controller is None else controller.copy()
        self.update_appearance_based_on_hp()

    def move(self):
        self.controller.update_based_on(self)
        if self.controller.is_moving:
            self.turn_to(self.controller.move_angle)
            super().move()


class ShootingUnit(Unit):
    def __init__(self, game_data: GameData, x: float, y: float,
                 targets: list[GameParticle], parent_list: list[GameParticle],
                 radius=10, speed=UNIT_SPEED * 2.5, hp=10, shoot_cd=10,
                 bullet_class=Bullet, **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, radius=radius, speed=speed, hp=hp, **kwargs)
        self.weapon_handler: WeaponHandler = WeaponHandler(self.game_data, self, ALL_MAIN_WEAPON_LIST[1])

    def move(self):
        super().move()
        if self.hp and self.controller.fire_main:
            self.weapon_handler.fire(self.controller.aim_angle)

class ShieldedUnit(Unit):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 shield_hp=None, shield_rad=None, **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, **kwargs)
        self.shoot_timer = 0
        shield_rad = shield_rad if shield_rad is not None else max(50, self.rad + 2 * self.hp)
        shield_hp = shield_hp if shield_hp is not None else 2 * self.hp
        self.parent_list.append(Shield(game_data, x, y, shield_rad, color=self.color,
                                       hp=shield_hp, parent=self, regen_rate=shield_hp / 50))

class SpawningUnit(Unit):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 child_class: type=Unit, child_kwargs: Optional[dict]=None,
                 child_speed: tuple[float, float] = (UNIT_SPEED * 2.5, UNIT_SPEED * 5),
                 child_spawn_cd=1000, **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, **kwargs)
        self.child_class = child_class
        self.child_kwargs = {} if child_kwargs is None else child_kwargs
        self.child_speed = child_speed
        self.child_count = 0
        self.child_spawn_cd = child_spawn_cd

    def move(self):
        super().move()
        self.spawn_with_cd()

    def spawn_with_cd(self):
        max_cap = (self.hp / self.max_hp) * (self.score / 1000)
        spawn_cd = (self.child_spawn_cd * self.max_hp / self.hp)

        if self.child_count < max_cap:
            self.child_count += max_cap / spawn_cd
        # max_cap - 1: only spawn when is hit (hp decrease)
        # max_cap: can spawn naturally
        # if self.child_count < max_cap - 1:
        #     return
        if not self.controller.fire_sub:
            return
        self.spawn_childs(int(self.child_count))
        self.child_count -= int(self.child_count)

    def spawn_childs(self, total: int, **kwargs):
        total = min(MAX_ENEMY_COUNT - len(self.parent_list), total)
        for i in range(int(total)):
            angle = i / total * math.pi * 2
            x = self.x + math.cos(angle) * (UNIT_RADIUS * 3 * (i % 3) + self.rad)
            y = self.y + math.sin(angle) * (UNIT_RADIUS * 3 * (i % 3) + self.rad)
            child: Unit = self.child_class(self.game_data, x, y, self.target_list, self.parent_list,
                                     speed=random.uniform(self.child_speed[0], self.child_speed[1]),
                                     angle=angle,
                                     color=self.color,
                                     **kwargs, **self.child_kwargs)
            child.angle = angle
            child.move()
            self.parent_list.append(child)

    def on_death(self):
        self.spawn_childs(self.child_count)
        return super().on_death()

class EliteUnit(ShootingUnit, ShieldedUnit):
    pass

class UnitMothership(ShootingUnit, ShieldedUnit, SpawningUnit):
    pass


