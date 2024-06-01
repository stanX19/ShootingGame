import math

import pygame
import utils
from enemy import Enemy
from constants import *


class Missile:
    def __init__(self, x, y, angle, enemies_list, target: [Enemy, None] = None, radius=MISSILE_RADIUS,
                 speed=MISSILE_SPEED, lifespan=60 * 2, hp=1, dmg=10):
        self.x = x
        self.y = y
        self.xv = math.cos(angle) * PLAYER_SPEED
        self.yv = math.sin(angle) * PLAYER_SPEED
        self.rad = radius
        self.angle = angle
        self.lifespan = lifespan  # fps * seconds
        self.target = target
        self.enemies_list = enemies_list
        self.reached_target = False
        self.hp = hp
        self.dmg = dmg
        self.speed = speed

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, MISSILE_COLOR, (int(self.x), int(self.y)), self.rad)

    def find_target(self):
        search_radius = 200
        hypot = math.hypot(self.xv, self.yv)
        dy = self.yv * search_radius / hypot
        dx = self.xv * search_radius / hypot
        self.target = Missile.find_target_at(self.x + dx, self.y + dy, self.enemies_list, search_radius)

    @staticmethod
    def find_target_at(x, y, enemy_list, search_radius=100.0):
        lowest_distance = search_radius
        target = None
        for enemy in enemy_list:
            y_dis = enemy.y - y
            x_dis = enemy.x - x
            distance = math.hypot(x_dis, y_dis)
            if distance < lowest_distance + enemy.rad:
                lowest_distance = distance
                target = enemy
        return target

    def angle_with(self, other):
        try:
            y_dis = other.y - self.y
            x_dis = other.x - self.x
            return self.angle - math.atan2(y_dis, x_dis)
        except AttributeError:
            return 0

    def calculate_intercept_angle(self, target):
        tx = target.x
        ty = target.y
        tvx = target.xv
        tvy = target.yv
        dx = tx - self.x
        dy = ty - self.y
        target_speed = math.hypot(tvx, tvy)
        a = target_speed ** 2 - (self.speed * 0.1) ** 2
        b = 2 * (dx * tvx + dy * tvy)
        c = dx ** 2 + dy ** 2
        disc = b ** 2 - 4 * a * c

        if disc < 0:
            return math.atan2(dy, dx)
        t1 = (-b + math.sqrt(disc)) / (2 * a)
        t2 = (-b - math.sqrt(disc)) / (2 * a)
        t = min(t1, t2) if t1 > 0 and t2 > 0 else max(t1, t2, 0)
        intercept_x = tx + tvx * t
        intercept_y = ty + tvy * t
        return math.atan2(intercept_y - self.y, intercept_x - self.x)

    def update(self):
        if self.target not in self.enemies_list:
            self.find_target()
        if self.lifespan <= 0:
            self.explode()
        if isinstance(self.target, Enemy):
            target_angle = self.calculate_intercept_angle(self.target)
            angle_diff = utils.angle_diff(target_angle, self.angle)
            angle_diff = utils.normalize(angle_diff, -math.pi / 24, math.pi / 24)
            self.angle += angle_diff
        self.xv = self.speed * math.cos(self.angle)
        self.yv = self.speed * math.sin(self.angle)
        magnitude = math.hypot(self.xv, self.yv)
        if magnitude > self.speed:
            self.xv = self.xv / magnitude * self.speed
            self.yv = self.yv / magnitude * self.speed

    def move(self):
        self.update()
        self.x += self.xv
        self.y += self.yv
        self.lifespan -= 1

    def explode(self):
        pass
