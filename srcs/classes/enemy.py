from __future__ import annotations
import pygame
import math
import random
from typing import Sequence, Optional
from srcs import utils
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.bullet import Bullet


class Enemy(GameParticle):
    def __init__(self, x, y, target: GameParticle, parent_list: list[GameParticle], radius=ENEMY_RADIUS,
                 speed=ENEMY_SPEED, angle=0.0, color=ENEMY_COLOR, hp=1, score=100, variable_shape=False):
        super().__init__(x, y, angle, speed, radius, color, hp, 1, score)
        self.variable_shape: bool = variable_shape
        self.target: GameParticle = target
        self.parent_list: list[GameParticle] = parent_list
        self.max_rad = None if radius == ENEMY_RADIUS else radius

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

        self.update_appearance_based_on_hp()

    def update_shape_based_on_hp(self):
        if self.variable_shape:
            self.rad = Enemy.get_rad(self.hp, self.max_hp, self.max_rad)

    def update_appearance_based_on_hp(self):
        self.update_shape_based_on_hp()
        self.dmg = 1  # / math.sqrt(self.max_hp)
        self.color = Enemy.get_color(self.hp, self.speed)

    @staticmethod
    def get_rad(hp: float, max_hp: float, max_rad: Optional[float]=None):
        max_rad = max_rad or ENEMY_RADIUS + max_hp - 1
        return ENEMY_RADIUS + (hp / max_hp) * max(0, max_rad - ENEMY_RADIUS)

    @staticmethod
    def get_color(hp: float, speed: float):
        return utils.color_norm((255, 105 - hp, 80 - hp + speed * 50))

    def on_death(self):
        pass


class DodgingEnemy(Enemy):
    def __init__(self, x, y, target: GameParticle, parent_list: list[GameParticle],
                 radius=10, speed=PLAYER_SPEED, hp=10, **kwargs):
        super().__init__(x, y, target, parent_list, radius=radius, speed=speed, hp=hp, **kwargs)
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


class ShootingEnemy(Enemy):
    def __init__(self, x, y, target: GameParticle, parent_list: list[GameParticle],
                 radius=10, speed=PLAYER_SPEED, hp=10, **kwargs):
        super().__init__(x, y, target, parent_list, radius=radius, speed=speed, hp=hp, **kwargs)
        self.shoot_cd = 0

    def move(self):
        super().move()
        self.shoot_cd -= 1
        if self.shoot_cd <= 0 and self.distance_with(self.target) <= ENEMY_SHOOT_RANGE:
            self.shoot()
            self.shoot_cd = 10 * self.max_hp / self.hp

    def shoot(self):
        self.parent_list.append(Bullet(
            self.x, self.y, self.angle_with(self.target), speed=BULLET_SPEED, rad=ENEMY_BULLET_RAD,
            dmg=self.target.max_hp / PLAYER_HP,
            color=ENEMY_BULLET_COLOR
        ))


class EliteEnemy(ShootingEnemy, DodgingEnemy):
    pass


class EnemyMothership(Enemy):
    def __init__(self, x, y, target: GameParticle, parent_list: list[GameParticle], **kwargs):
        super().__init__(x, y, target, parent_list, **kwargs)
        self.dodge_angle: float = random.choice([math.pi / 2, -math.pi / 2])
        self.child_speed = (PLAYER_SPEED, PLAYER_SPEED * 2)
        self.child_count = 0

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

    def move(self):
        super().move()
        self.spawn_with_cd()

    def spawn_with_cd(self):
        max_cap = (self.hp / self.max_hp) * (self.score / 1000)
        spawn_cd = 1000  # (1000 * self.max_hp / self.hp)

        if self.child_count + max_cap / spawn_cd < max_cap:  # cannot reach max_cap naturally
            self.child_count += max_cap / spawn_cd
        if self.child_count < max_cap:  # only false when is hit (hp decrease)
            return
        if self.distance_with(self.target) > ENEMY_SHOOT_RANGE:
            return
        self.spawn_childs(int(self.child_count))
        self.child_count = 0

    def spawn_childs(self, total: int, _cls=Enemy, **kwargs):
        total = min(MAX_ENEMY_COUNT - len(self.parent_list), total)
        for i in range(int(total)):
            angle = i / total * math.pi * 2
            x = self.x + math.cos(angle) * (ENEMY_RADIUS * 3 * (i % 3) + self.rad)
            y = self.y + math.sin(angle) * (ENEMY_RADIUS * 3 * (i % 3) + self.rad)
            child = _cls(x, y, self.target, self.parent_list, variable_shape=True,
                         speed=random.uniform(self.child_speed[0], self.child_speed[1]), **kwargs)
            child.angle = angle
            child.move()
            self.parent_list.append(child)

    def on_death(self):
        self.spawn_childs(self.child_count)
        super().on_death()
