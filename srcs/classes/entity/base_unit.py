from __future__ import annotations

import math
from ctypes import wstring_at
from typing import Optional

import pygame
import random

from srcs import utils
from srcs.classes import algo
from srcs.classes.entity.breakable import Breakable, Debris
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.effect import Effect
from srcs.classes.entity.shield import Shield
from srcs.classes.faction_data import FactionData
from srcs.classes.game_data import GameData
from srcs.constants import *
from srcs.utils import color_mix


class BaseUnit(Breakable):
    def __init__(self, faction: FactionData,
                 x: float = 0.0, y: float = 0.0,
                 angle=0.0, speed=UNIT_SPEED, radius=UNIT_RADIUS, color=ENEMY_COLOR,
                 hp=1, dmg=1, score=10, variable_shape=True, variable_color=True,
                 shoot_range: float=UNIT_SHOOT_RANGE, bullet_speed: float=BULLET_SPEED,
                 # importance:int=0,
                 **kwargs):
        super().__init__(faction, x, y, angle, speed, radius, color, hp, dmg, score, **kwargs)
        self.max_speed: float = speed
        self.target: Optional[GameParticle] = None
        self.warned_target: bool = False
        self.variable_shape: bool = variable_shape
        self.variable_color: bool = variable_color
        self.original_color: tuple = color
        self.shoot_range: float = shoot_range
        self.bullet_speed: float = bullet_speed
        self.max_rad: float = radius
        # self.importance: int = importance

        self.update_appearance_based_on_hp()

    def find_new_target(self):
        """Find the closest target from the list of target_list."""
        return self.find_new_target_at(self.x, self.y)

    def find_new_target_at(self, x, y, distance_limit=float('inf')):
        # Find the closest target
        targets: list[GameParticle] = [i for i in self.faction.target_list if self.faction.game_data.in_map(i)]
        closest_target = None
        min_distance = float('inf')

        K = MAP_WIDTH + MAP_HEIGHT
        for target in targets:
            dis = target.distance_with_cord(x, y)
            if dis > distance_limit:
                continue
            if isinstance(target, (Bullet, Debris)) and not algo.can_catch_up(self, target):
                continue
            distance = (
               dis
               # - K * utils.sigmoid(target.score + target.base_score, 30000) # 30000 will reach 0.9
               - (isinstance(target, BaseUnit) or isinstance(target, Shield)) * 2 * K
               - self.is_targeting_self(target) * 3 * K
               - (isinstance(self.parent, BaseUnit) and self.parent.is_targeting_self(target)) * 4 * K
               - (dis < self.shoot_range) * 5 * K
            )
            if distance < min_distance:
                min_distance = distance
                closest_target = target

        self.target = closest_target
        self.warned_target = False

    def is_targeting_self(self, other: GameParticle):
        return isinstance(other, BaseUnit) and other.target is self

    def turn_to(self, new_angle, lerp=0.1):
        turn_angle = new_angle - self.angle
        turn_angle = (turn_angle + math.pi) % (2 * math.pi) - math.pi
        self.angle += turn_angle * lerp
        self.angle = (self.angle + math.pi) % (2 * math.pi) - math.pi

    def move(self):
        super().move()
        while isinstance(self.parent, GameParticle) and self.parent.is_dead():
            self.parent = self.parent.parent
        self.update_appearance_based_on_hp()
        spd = self.speed
        if (self.x - self.rad < 0 and self.xv < 0) or (self.x + self.rad > MAP_WIDTH and self.xv > 0):
            self.xv = -self.xv
        if (self.y - self.rad < 0 and self.yv < 0) or (self.y + self.rad > MAP_HEIGHT and self.yv > 0):
            self.yv = -self.yv
        self.x = utils.clamp(self.x, self.rad, MAP_WIDTH - self.rad)
        self.y = utils.clamp(self.y, self.rad, MAP_HEIGHT - self.rad)
        self.speed = spd
        self.warn_target()

    def warn_target(self):
        if self.target and not self.warned_target and isinstance(self.target, BaseUnit) \
            and self.distance_with(self.target) < self.shoot_range:
            self.target.find_new_target()
            self.warned_target = True

    def update_rad(self):
        self.rad = BaseUnit.get_rad(self.hp, self.max_hp, self.max_rad)

    def update_color(self):
        self.color = BaseUnit.get_color(self.hp, self.speed, self.original_color)

    def update_appearance_based_on_hp(self):
        if self.variable_shape:
            self.update_rad()
        if self.variable_color:
            self.update_color()

    @staticmethod
    def get_rad(hp: float, max_hp: float, max_rad: Optional[float] = None):
        max_rad = max_rad or UNIT_RADIUS + max_hp - 1
        return int(UNIT_RADIUS + (hp / max_hp) * max(0, max_rad - UNIT_RADIUS))

    @staticmethod
    def get_color(hp: float, speed: float, base_color: tuple):
        r, g, b = base_color

        max_change = 100
        hp_factor = min(1.0, hp / 100)
        speed_factor = min((speed - UNIT_SPEED) / (PLAYER_SPEED - UNIT_SPEED), 1)
        b = b + max_change * speed_factor
        g = g - max_change * hp_factor

        return utils.color_norm((r, g, b))

    def on_death(self):
        self.faction.game_data.effects.append(Effect(self.faction.game_data, self.x, self.y, self.angle,
                                              speed=self.speed, rad=self.rad, lifespan=3,
                                              color=self.color, fade_off=True))
        return super().on_death()

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # draw_arrow(surface, (self.x, self.y), (self.target.x, self.target.y))

    def regen_hp(self, regen_amount: float):
        super().regen_hp(regen_amount)
