from __future__ import annotations
import pygame
import math
import random
from typing import Sequence, Optional
from srcs import utils
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.bullet import Bullet
from srcs.classes.effect import Effect
from srcs.classes.game_data import GameData


class Enemy(GameParticle):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 speed=ENEMY_SPEED, angle=0.0, radius=ENEMY_RADIUS, color=ENEMY_COLOR,
                 hp=1, dmg=1, score=100, variable_shape=True, variable_color=True):
        super().__init__(x, y, angle, speed, radius, color, hp, dmg, score)
        self.game_data: GameData = game_data
        self.variable_shape: bool = variable_shape
        self.variable_color: bool = variable_color
        self.targets: list[GameParticle] = targets
        self.target: Optional[GameParticle] = None
        self.parent_list: list[GameParticle] = parent_list
        self.max_rad = None if radius == ENEMY_RADIUS else radius

        # Initially find the closest target
        self.find_new_target()

        self.update_appearance_based_on_hp()

    def find_new_target(self):
        """Find the closest target from the list of targets."""
        if not self.targets:
            self.target = None
            return

        # Find the closest target
        targets = [i for i in self.targets if self.game_data.in_map(i)]
        closest_target = None
        min_distance = float('inf')

        for target in targets:
            distance = self.distance_with(target) + 1000 * isinstance(target, Bullet)
            if distance < min_distance:
                min_distance = distance
                closest_target = target

        self.target = closest_target

    def move(self):
        if self.target is None or self.target.is_dead():
            self.find_new_target()

        if self.target:
            dy = self.target.y - self.y
            dx = self.target.x - self.x
            dis = math.hypot(dy, dx)
            if dis > 0:
                dy /= dis
                dx /= dis
            spd = self.speed
            self.xv += dx
            self.yv += dy
            self.speed = spd

        super().move()
        self.update_appearance_based_on_hp()

    def update_appearance_based_on_hp(self):
        if self.variable_shape:
            self.rad = Enemy.get_rad(self.hp, self.max_hp, self.max_rad)
        if self.variable_color:
            self.color = Enemy.get_color(self.hp, self.speed)

    @staticmethod
    def get_rad(hp: float, max_hp: float, max_rad: Optional[float]=None):
        max_rad = max_rad or ENEMY_RADIUS + max_hp - 1
        return ENEMY_RADIUS + (hp / max_hp) * max(0, max_rad - ENEMY_RADIUS)

    @staticmethod
    def get_color(hp: float, speed: float):
        return utils.color_norm((255, 105 - hp, 80 - hp + speed * 50))

    def on_death(self):
        self.game_data.effects.append(Effect(self.game_data, self.x, self.y, self.angle,
                                             speed=self.speed, rad=self.rad, lifespan=3,
                                             color=self.color, fade_off=True))
        return super().on_death()


class DodgingEnemy(Enemy):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 radius=10, speed=PLAYER_SPEED, hp=10, **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, radius=radius, speed=speed, hp=hp, **kwargs)
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
            if discriminant >= 0 and a:
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
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 radius=10, speed=PLAYER_SPEED, hp=10, **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, radius=radius, speed=speed, hp=hp, **kwargs)
        self.shoot_cd = 0

    def move(self):
        super().move()
        self.shoot_cd -= 1
        if self.target and self.shoot_cd <= 0 and self.distance_with(self.target) <= ENEMY_SHOOT_RANGE:
            self.shoot()
            self.shoot_cd = 10 * self.max_hp / self.hp

    def shoot(self):
        # Get the current position and velocity of the target
        target_x, target_y = self.target.x, self.target.y
        target_xv, target_yv = self.target.xv, self.target.yv

        # Calculate the distance to the target
        distance = self.distance_with(self.target)

        # Bullet speed (constant)
        bullet_speed = BULLET_SPEED

        # Solve for the lead time: time = distance / relative speed
        # We use an iterative method to find the future point where the bullet can hit
        # it accounts for the fact that the target is moving and the bullet is too.

        lead_time = 0.0
        lead_x = 0
        lead_y = 0

        try:
            # find distance -> find time needed to hit -> predict target location -> repeat
            for _ in range(10):
                lead_x = target_x + target_xv * lead_time
                lead_y = target_y + target_yv * lead_time
                future_distance = math.hypot(lead_x - self.x, lead_y - self.y)
                lead_time = future_distance / bullet_speed

            lead_angle = math.atan2(lead_y - self.y, lead_x - self.x)

        except ZeroDivisionError:
            lead_angle = self.angle_with(self.target)

        self.parent_list.append(Bullet(
            self.game_data, self.x, self.y, lead_angle, speed=bullet_speed, rad=ENEMY_BULLET_RAD,
            color=self.color
        ))


class EliteEnemy(ShootingEnemy, DodgingEnemy):
    pass


class EnemyMothership(Enemy):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle], **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, **kwargs)
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
            child = _cls(self.game_data, x, y, self.targets, self.parent_list, variable_shape=True,
                         speed=random.uniform(self.child_speed[0], self.child_speed[1]), **kwargs)
            child.angle = angle
            child.move()
            self.parent_list.append(child)

    def on_death(self):
        self.spawn_childs(self.child_count)
        return super().on_death()
