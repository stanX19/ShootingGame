from __future__ import annotations

from typing import Optional

import pygame

from srcs import utils
from srcs.classes.controller import BaseController, AIController, SmartAIController
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.shield import Shield
from srcs.classes.faction_data import FactionData
from srcs.classes.weapon_classes.general_weapon import BaseWeapon
from srcs.classes.weapon_classes.weapon_handler import WeaponHandler
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum
from srcs.constants import *


class Unit(BaseUnit):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 controller: Optional[BaseController] = None, radius=10, speed=UNIT_SPEED * 2.5, hp=1,
                 weapons: list[BaseWeapon] | BaseWeapon | None = None,
                 sub_weapons: list[BaseWeapon] | BaseWeapon | None = None,
                 shield_hp: float = 0, shield_rad: float = 0, **kwargs):
        super().__init__(faction, x, y, angle, radius=radius, speed=speed, hp=hp, **kwargs)
        self.controller: BaseController = AIController() if controller is None else controller.copy()
        self.update_appearance_based_on_hp()
        self.main_weapon: WeaponHandler = WeaponHandler(self, weapons)
        self.sub_weapon: WeaponHandler = WeaponHandler(self, sub_weapons)
        self.shield: Shield | None = None

        # Shield
        if shield_hp != 0 and shield_rad == 0:
            shield_rad = self.rad + shield_hp
            print("Warning: Undefined shield_rad when shield_hp is non-zero")
        if shield_hp == 0:
            shield_hp = 1
            shield_rad = 0
        self._spawn_shield(shield_hp, shield_rad)

    def _spawn_shield(self, shield_hp, shield_rad):
        self.shield = Shield(self.faction, self.x, self.y, rad=shield_rad, color=utils.color_mix(self.color, Shield.default_color),
                             hp=shield_hp, parent=self, regen_rate=shield_hp / 50)
        self.faction.parent_list.append(self.shield)

    def move(self):
        super().move()
        if not self.controller.is_moving:
            self.speed = 0
        else:
            self.speed = self.max_speed
        self.turn_to(self.controller.move_angle)

        if self.main_weapon.weapon is not None:
            self.bullet_speed = self.main_weapon.weapon.get_speed(self)
        if self.hp and self.controller.fire_main:
            self.main_weapon.fire(self.controller.aim_x, self.controller.aim_y)
        if self.hp and self.controller.fire_sub:
            self.sub_weapon.fire(self.controller.aim_x, self.controller.aim_y)
        self.controller.update_based_on(self)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # pygame.draw.circle(surface, (0, 255, 0), (int(self.x), int(self.y)), self.shoot_range, width=2)
        # draw_arrow(surface, (self.x, self.y), (self.target.x, self.target.y), (255, 255, 255), 3)

    # def __str__(self):
    #     return super().__str__() + f" {self.controller.__class__.__name__}"
