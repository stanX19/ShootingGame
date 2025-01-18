from __future__ import annotations
import pygame
import math
import random
from typing import Optional

from srcs import utils
from srcs.classes.entity.shield import Shield
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.faction_data import FactionData
from srcs.classes.weapon_handler import WeaponHandler
from srcs.classes.weapons import WeaponType, MainWeaponEnum
from srcs.constants import *
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.controller import BaseController, AIController


class Unit(BaseUnit):
    def __init__(self, faction: FactionData, x: float, y: float,
                 controller: Optional[BaseController] = None, **kwargs):
        super().__init__(faction, x, y, **kwargs)
        self.controller: BaseController = AIController() if controller is None else controller.copy()
        self.update_appearance_based_on_hp()

    def move(self):
        super().move()
        self.controller.update_based_on(self)
        if not self.controller.is_moving:
            self.speed = 0
        else:
            self.speed = self.max_speed
        self.turn_to(self.controller.move_angle)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # draw_arrow(surface, (self.x, self.y), (self.target.x, self.target.y), (255, 255, 255), 3)


class ShootingUnit(Unit):
    def __init__(self, faction: FactionData, x: float, y: float,
                 radius=10, speed=UNIT_SPEED * 2.5, hp=10,
                 weapons: list[WeaponType] | None = MainWeaponEnum.machine_gun,
                 sub_weapons: list[WeaponType] | None = None, **kwargs):
        super().__init__(faction, x, y, radius=radius, speed=speed, hp=hp, **kwargs)
        self.main_weapon: WeaponHandler = WeaponHandler(self, weapons)
        self.sub_weapon: WeaponHandler = WeaponHandler(self, sub_weapons)

    def move(self):
        super().move()
        try:
            self.bullet_speed = max(self.speed - self.main_weapon.weapon.recoil, self.main_weapon.weapon.speed)
        except AttributeError:
            pass
        if self.hp and self.controller.fire_main:
            self.main_weapon.fire(self.controller.aim_x, self.controller.aim_y)
        if self.hp and self.controller.fire_sub:
            self.sub_weapon.fire(self.controller.aim_x, self.controller.aim_y)

class ShieldedUnit(Unit):
    def __init__(self, faction: FactionData, x: float, y: float,
                 shield_hp=None, shield_rad=None, **kwargs):
        super().__init__(faction, x, y, **kwargs)
        self.shoot_timer = 0
        shield_rad = shield_rad if shield_rad is not None else max(50, self.rad + 2 * self.hp)
        shield_hp = shield_hp if shield_hp is not None else 2 * self.hp
        self.faction.parent_list.append(Shield(faction, x, y, shield_rad, color=utils.color_mix(self.color, Shield.default_color),
                                        hp=shield_hp, parent=self, regen_rate=shield_hp / 50))

class SpawningUnit(Unit):
    def __init__(self, faction: FactionData, x: float, y: float,
                 child_class: type=Unit, child_kwargs: Optional[dict]=None,
                 child_speed: tuple[float, float] = (UNIT_SPEED * 2.5, UNIT_SPEED * 5),
                 child_spawn_cd=1000, **kwargs):
        super().__init__(faction, x, y, **kwargs)
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
        total = min(MAX_ENEMY_COUNT - len(self.faction.parent_list), total)
        for i in range(int(total)):
            angle = i / total * math.pi * 2
            x = self.x + math.cos(angle) * (UNIT_RADIUS * 3 * (i % 3) + self.rad)
            y = self.y + math.sin(angle) * (UNIT_RADIUS * 3 * (i % 3) + self.rad)
            child: Unit = self.child_class(self.faction.game_data, x, y, self.faction.target_list, self.faction.parent_list,
                                     speed=random.uniform(self.child_speed[0], self.child_speed[1]),
                                     angle=angle,
                                     color=self.color,
                                     controller=self.controller.get_child(),
                                     **kwargs, **self.child_kwargs)
            child.angle = angle
            child.move()
            self.faction.parent_list.append(child)

    def on_death(self):
        self.spawn_childs(self.child_count)
        return super().on_death()



