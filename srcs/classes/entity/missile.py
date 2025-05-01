from __future__ import annotations
import math

import pygame

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
        if self.distance_with(self.target) < 0:
            self.kill()
        if self.target not in self.faction.target_list:
            self.find_target()
            self._warned_target = False
        if isinstance(self.target, GameParticle):
            target_angle = calculate_intercept_angle(self, self.target)
            angle_diff = utils.angle_diff(target_angle, self.angle)
            angle_diff = utils.clamp(angle_diff, -math.pi / 24, math.pi / 24)
            self.angle += angle_diff

        if (not self._warned_target and isinstance(self.target, BaseUnit)
                and self.distance_with(self.target) + self.target.rad < self.target.shoot_range):
            self.target.find_new_target()
            self._warned_target = True

    def move(self):
        self.update()
        super().move()

    def draw(self, surface: pygame.Surface):
        # Draw the fire ball (orange circle behind)
        fire_ball_center_x = self.x - math.cos(self.angle) * self.rad * 0.75 # Adjust offset
        fire_ball_center_y = self.y - math.sin(self.angle) * self.rad * 0.75 # Adjust offset
        pygame.draw.circle(surface, FLAME_COLOR, (int(fire_ball_center_x), int(fire_ball_center_y)),
                           int(self.rad * 0.5)) # Adjust size
        missile_center_x = self.x + math.cos(self.angle) * self.rad * 0.25  # Adjust offset
        missile_center_y = self.y + math.sin(self.angle) * self.rad * 0.25  # Adjust offset
        pygame.draw.circle(surface, self.color, (int(missile_center_x), int(missile_center_y)),
                           int(self.rad * 0.75))  # Adjust size
        # # Draw the triangle representing the missile
        # triangle_points = []
        #
        # # Front point: further out to make it pointy
        # front_point_x = self.x + math.cos(self.angle) * self.rad
        # front_point_y = self.y + math.sin(self.angle) * self.rad
        # triangle_points.append((int(front_point_x), int(front_point_y)))
        #
        # # Rear points: on the radius
        # rear_angle1 = self.angle + math.pi * 0.7 # Slightly adjust the angle for a better triangle
        # rear_angle2 = self.angle - math.pi * 0.7 # Slightly adjust the angle for a better triangle
        #
        # rear_point1_x = self.x + math.cos(rear_angle1) * self.rad
        # rear_point1_y = self.y + math.sin(rear_angle1) * self.rad
        # triangle_points.append((int(rear_point1_x), int(rear_point1_y)))
        #
        # rear_point2_x = self.x + math.cos(rear_angle2) * self.rad
        # rear_point2_y = self.y + math.sin(rear_angle2) * self.rad
        # triangle_points.append((int(rear_point2_x), int(rear_point2_y)))
        #
        # pygame.draw.polygon(surface, self.color, triangle_points)