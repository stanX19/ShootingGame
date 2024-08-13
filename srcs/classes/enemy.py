from __future__ import annotations
import pygame
import math
import random
from typing import Sequence
from srcs import utils
from srcs.constants import *
from srcs.classes.game_particle import GameParticle


class Enemy(GameParticle):
    def __init__(self, x, y, target: GameParticle, parent_list: list[GameParticle], radius=ENEMY_RADIUS,
                 speed=ENEMY_SPEED, angle=0.0, color=ENEMY_COLOR, hp=1, score=100, variable_shape=False):
        super().__init__(x, y, angle, speed, radius, color, hp, 1)
        self.score: float = score
        self.variable_shape: bool = variable_shape
        self.target: GameParticle = target
        self.parent_list: list[GameParticle] = parent_list

        if variable_shape:
            self.update_appearance_based_on_hp()

    def move(self):
        dy = self.target.y - self.y
        dx = self.target.x - self.x
        dis = math.hypot(dy, dx)
        dy /= dis
        dx /= dis
        spd = self.speed
        self.xv += dx
        self.yv += dy
        self.speed = spd
        super().move()

        if self.variable_shape:
            self.update_appearance_based_on_hp()

    def update_appearance_based_on_hp(self):
        self.rad = Enemy.get_rad(self.hp)
        self.color = Enemy.get_color(self.hp, self.speed)

    @staticmethod
    def get_rad(hp: float):
        return ENEMY_RADIUS + (hp - 1)

    @staticmethod
    def get_color(hp: float, speed: float):
        return utils.color_norm((255, 105 - hp, 80 - hp + speed * 50))

    def on_death(self):
        pass


class EliteEnemy(Enemy):
    def __init__(self, x, y, target: GameParticle, parent_list: list[GameParticle],
                 radius=10, speed=PLAYER_SPEED, **kwargs):
        super().__init__(x, y, target, parent_list, radius=radius, speed=speed, **kwargs)
        self.dodge_angle: float = random.choice([math.pi / 2, -math.pi / 2])

    def dodge_bullets(self, bullets: Sequence[GameParticle]):
        closest_bullet = None
        min_time_to_collision = float('inf')

        MAX_DISTANCE = 100
        MAX_CHECK = 200

        # more than this will cause lag
        for bullet in bullets[:MAX_CHECK]:
            # Calculate relative position and velocity
            rel_x = bullet.x - self.x
            rel_y = bullet.y - self.y

            # if math.hypot(rel_x, rel_y) < MAX_DISTANCE:
            #     continue

            rel_vx = bullet.xv - self.xv
            rel_vy = bullet.yv - self.yv

            # Calculate the time to the closest approach
            a = rel_vx ** 2 + rel_vy ** 2
            b = 2 * (rel_x * rel_vx + rel_y * rel_vy)
            c = rel_x ** 2 + rel_y ** 2 - (100 + self.rad + bullet.rad) ** 2

            # Quadratic formula to find the smallest positive time to collision
            discriminant = b ** 2 - 4 * a * c
            if discriminant >= 0:
                t1 = (-b - math.sqrt(discriminant)) / (2 * a)
                t2 = (-b + math.sqrt(discriminant)) / (2 * a)
                t_collision = min(t1, t2) if t1 > 0 else t2

                if 0 < t_collision < min_time_to_collision:
                    min_time_to_collision = t_collision
                    closest_bullet = bullet
                    break

        if closest_bullet and min_time_to_collision < float('inf'):
            angle = math.atan2(closest_bullet.yv, closest_bullet.xv) + self.dodge_angle
            dodge_xv = self.speed * math.cos(angle)
            dodge_yv = self.speed * math.sin(angle)

            self.x += dodge_xv
            self.y += dodge_yv
            return True
        return False


class EnemyMothership(Enemy):
    def draw(self, surface: pygame.Surface):
        super().draw(surface)

    def move(self):
        super(EnemyMothership, self).move()

    def on_death(self):
        total = int(self.score / 500)
        # if len(self.parent_list) + total > 300:
        #     return
        for i in range(total):
            angle = -math.pi + i / total * math.pi * 2
            x = self.x + math.cos(angle) * total * (i % 3 + 1)
            y = self.y + math.sin(angle) * total * (i % 3 + 1)
            child = Enemy(x, y, self.target, self.parent_list, hp=1, variable_shape=True, speed=PLAYER_SPEED)
            child.angle = angle
            child.move()
            self.parent_list.append(child)
        super().on_death()
