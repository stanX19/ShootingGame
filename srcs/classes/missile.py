from __future__ import annotations
import math
from srcs import utils
from srcs.classes.explosive import Explosive, Bullet
from srcs.classes.game_particle import GameParticle
from srcs.classes.algo import calculate_intercept_angle
from srcs.constants import *
from srcs.classes.game_data import GameData


class Missile(Explosive):
    def __init__(self, game_data: GameData, x: float, y: float, angle: float, enemies_list: list[GameParticle],
                 target: [GameParticle, None] = None,
                 radius=MISSILE_RADIUS,
                 speed=MISSILE_SPEED,
                 hp=1, dmg=10, lifespan=60 * 2):
        super().__init__(game_data, x, y, angle, radius, speed, hp, dmg, lifespan, MISSILE_COLOR, MISSILE_COLOR)
        self.game_data: GameData = game_data
        self.target: [GameParticle, None] = target
        self.enemies_list: list[GameParticle] = enemies_list
        self.reached_target: bool = False

    def find_target(self):
        search_radius = 200
        hypot = math.hypot(self.xv, self.yv)
        dy = self.yv * search_radius / hypot
        dx = self.xv * search_radius / hypot
        self.target = Missile.find_target_at(self.x + dx, self.y + dy, self.enemies_list, search_radius)

    @staticmethod
    def find_target_at(x: float, y: float, target_list: list[GameParticle], search_radius=100.0):
        lowest_distance = search_radius
        target = None
        for enemy in target_list:
            y_dis = enemy.y - y
            x_dis = enemy.x - x
            distance = math.hypot(x_dis, y_dis) + 1000 * isinstance(enemy, Bullet)
            if distance < lowest_distance + enemy.rad:
                lowest_distance = distance
                target = enemy
        return target

    def update(self):
        if self.target not in self.enemies_list:
            self.find_target()
        if isinstance(self.target, GameParticle):
            target_angle = calculate_intercept_angle(self, self.target)
            angle_diff = utils.angle_diff(target_angle, self.angle)
            angle_diff = utils.normalize(angle_diff, -math.pi / 24, math.pi / 24)
            self.angle += angle_diff

    def move(self):
        self.update()
        super().move()

