from __future__ import annotations
import math
from srcs import utils
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.explosive import Explosive
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.algo import calculate_intercept_angle
from srcs.classes.faction_data import FactionData
from srcs.constants import *


class Missile(Explosive):
    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0,
                 speed=MISSILE_SPEED,
                 radius=MISSILE_RADIUS,
                 color=MISSILE_COLOR,
                 hp=1, dmg=10, lifespan=360 * 2,
                 target: [GameParticle, None] = None,
                 **kwargs):
        super().__init__(faction, x, y, angle, speed, radius, color, hp, dmg, lifespan, **kwargs)
        self.target: [GameParticle, None] = target
        self.reached_target: bool = False
        self._warned_target = False

    def find_target(self):
        search_radius = 200
        hypot = math.hypot(self.xv, self.yv)
        dy = self.yv * search_radius / hypot
        dx = self.xv * search_radius / hypot
        self.target = Missile.find_target_at(self.x + dx, self.y + dy, self.faction.target_list, search_radius)

    @staticmethod
    def find_target_at(x: float, y: float, target_list: list[GameParticle], search_radius=100.0):
        lowest_distance = search_radius
        target = None
        for enemy in target_list:
            y_dis = enemy.y - y
            x_dis = enemy.x - x
            distance = math.hypot(x_dis, y_dis) - 2000 * isinstance(enemy, BaseUnit) - enemy.rad
            if distance < lowest_distance:
                lowest_distance = distance
                target = enemy
        return target

    def update(self):
        if self.target not in self.faction.target_list:
            self.find_target()
            self._warned_target = False
        if isinstance(self.target, GameParticle):
            target_angle = calculate_intercept_angle(self, self.target)
            angle_diff = utils.angle_diff(target_angle, self.angle)
            angle_diff = utils.clamp(angle_diff, -math.pi / 24, math.pi / 24)
            self.angle += angle_diff
        # TODO:
        #  combine warn target from base_unit
        if not self._warned_target and isinstance(self.target, BaseUnit) and self.distance_with(self.target) < self.target.shoot_range:
            self.target.find_new_target()
            self._warned_target = True

    def move(self):
        self.update()
        super().move()

