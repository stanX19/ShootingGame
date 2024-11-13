from __future__ import annotations

from typing import Optional

import pygame

from srcs import utils
from srcs.classes import algo
from srcs.classes.bullet import Bullet
from srcs.classes.effect import Effect
from srcs.classes.game_data import GameData
from srcs.classes.game_particle import GameParticle
from srcs.constants import *


class BaseUnit(GameParticle):
    def __init__(self, game_data: GameData, x: float, y: float, targets: list[GameParticle], parent_list: list[GameParticle],
                 speed=UNIT_SPEED, angle=0.0, radius=UNIT_RADIUS, color=ENEMY_COLOR,
                 hp=1, dmg=1, score=100, variable_shape=True, variable_color=True,
                 shoot_range: float=UNIT_SHOOT_RANGE, bullet_speed: float=BULLET_SPEED):
        super().__init__(x, y, angle, speed, radius, color, hp, dmg, score)
        self.game_data: GameData = game_data
        self.parent_list: list[GameParticle] = parent_list
        self.target_list: list[GameParticle] = targets
        self.target: Optional[GameParticle] = None
        self.warned_target: bool = False
        self.variable_shape: bool = variable_shape
        self.variable_color: bool = variable_color
        self.original_color: tuple = color
        self.shoot_range: float = shoot_range
        self.bullet_speed: float = bullet_speed
        self.max_rad: float = None if radius == UNIT_RADIUS else radius

        self.update_appearance_based_on_hp()

    def find_new_target(self):
        """Find the closest target from the list of target_list."""
        if not self.target_list:
            self.target = None
            return

        # Find the closest target
        targets = [i for i in self.target_list if self.game_data.in_map(i)]
        closest_target = None
        min_distance = float('inf')

        K = self.shoot_range
        for target in targets:
            if isinstance(target, Bullet) and not algo.can_catch_up(self, target):
                continue
            dis = self.distance_with(target)
            distance = dis\
                       + isinstance(target, Bullet) * 2 * K\
                       - target.dmg * 10\
                       - (dis < self.shoot_range) * K \
                       - (isinstance(target, BaseUnit) and target.target is self) * 2 * K
            if distance < min_distance:
                min_distance = distance
                closest_target = target

        self.target = closest_target
        self.warned_target = False

    def turn_to(self, new_angle, lerp=0.1):
        # turn_angle = new_angle - self.angle
        # self.angle += turn_angle * lerp
        self.angle = new_angle

    def move(self):
        self.update_appearance_based_on_hp()
        spd = self.speed
        if (self.x - self.rad < 0 and self.xv < 0) or (self.x + self.rad > MAP_WIDTH and self.xv > 0):
            self.xv = 0
        if (self.y - self.rad < 0 and self.yv < 0) or (self.y + self.rad > MAP_HEIGHT and self.yv > 0):
            self.yv = 0
        self.speed = spd
        super().move()
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
        self.game_data.effects.append(Effect(self.game_data, self.x, self.y, self.angle,
                                             speed=self.speed, rad=self.rad, lifespan=3,
                                             color=self.color, fade_off=True))
        return super().on_death()

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # draw_arrow(surface, (self.x, self.y), (self.target.x, self.target.y))
