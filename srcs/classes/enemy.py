from __future__ import annotations
import pygame
import math
import random
from typing import Sequence, Optional

from numpy.lib.function_base import angle

from srcs import utils
from srcs.classes.shield import Shield
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.bullet import Bullet
from srcs.classes.effect import Effect
from srcs.classes.game_data import GameData
from srcs.classes.draw_utils import draw_arrow
from srcs.classes import algo


class Enemy(GameParticle):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 speed=UNIT_SPEED, angle=0.0, radius=UNIT_RADIUS, color=ENEMY_COLOR,
                 hp=1, dmg=1, score=100, variable_shape=True, variable_color=True,
                 shoot_range=UNIT_SHOOT_RANGE):
        super().__init__(x, y, angle, speed, radius, color, hp, dmg, score)
        self.game_data: GameData = game_data
        self.variable_shape: bool = variable_shape
        self.variable_color: bool = variable_color
        self.original_color: tuple = color
        self.target_list: list[GameParticle] = targets
        self.target: Optional[GameParticle] = None
        self.warned_target: bool = False
        self.parent_list: list[GameParticle] = parent_list
        self.max_rad = None if radius == UNIT_RADIUS else radius
        self.shoot_range = shoot_range

        self.find_new_target()

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
                       - (isinstance(target, Enemy) and target.target is self) * 2 * K
            if distance < min_distance:
                min_distance = distance
                closest_target = target

        self.target = closest_target
        self.warned_target = False

    def turn_to(self, new_angle, lerp=0.1):
        # turn_angle = new_angle + math.pi - self.angle
        # self.angle += turn_angle * lerp
        self.angle = new_angle

    def move(self):
        if self.target is None or self.target.is_dead():
            self.find_new_target()

        if self.target:
            self.turn_to(self.angle_with(self.target))
            if not self.warned_target and isinstance(self.target, Enemy)\
                    and self.distance_with(self.target) < self.shoot_range:
                self.target.find_new_target()
                self.warned_target = True

        spd = self.speed
        if (self.x - self.rad < 0 and self.xv < 0) or (self.x + self.rad > MAP_WIDTH and self.xv > 0):
            self.xv = 0
        if (self.y - self.rad < 0 and self.yv < 0) or (self.y + self.rad > MAP_HEIGHT and self.yv > 0):
            self.yv = 0
        self.speed = spd
        super().move()
        self.update_appearance_based_on_hp()

    def update_rad(self):
        self.rad = Enemy.get_rad(self.hp, self.max_hp, self.max_rad)

    def update_color(self):
        self.color = Enemy.get_color(self.hp, self.speed, self.original_color)

    def update_appearance_based_on_hp(self):
        if self.variable_shape:
            self.update_rad()
        if self.variable_color:
            self.update_color()

    @staticmethod
    def get_rad(hp: float, max_hp: float, max_rad: Optional[float]=None):
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

        if closest_bullet and min_time_to_collision < self.shoot_range:
            rel_xv = closest_bullet.xv
            rel_yv = closest_bullet.yv
            self.turn_to(math.atan2(rel_yv, rel_xv) + self.dodge_angle, lerp=0.3)
            return True
        return False

    def move(self):
        self.dodge_bullets(self.target_list)
        super().move()


class ShootingEnemy(Enemy):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 radius=10, speed=PLAYER_SPEED, hp=10, shoot_cd=10, bullet_speed=BULLET_SPEED,
                 bullet_class=Bullet, **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, radius=radius, speed=speed, hp=hp, **kwargs)
        self.shoot_timer = 0
        self.shoot_cd = shoot_cd
        self.bullet_speed = bullet_speed
        self.bullet_class = bullet_class

    def move(self):
        super().move()
        self.shoot_timer -= 1
        if (self.target and self.shoot_timer <= 0
                and self.distance_with(self.target) <= self.shoot_range and self.hp):
            self.shoot()
            self.shoot_timer = self.shoot_cd * self.max_hp / self.hp

    def shoot(self):
        # Get the current position and velocity of the target
        target_x, target_y = self.target.x, self.target.y
        target_xv, target_yv = self.target.xv, self.target.yv

        # Bullet speed (constant)
        bullet_speed = self.bullet_speed

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

        self.parent_list.append(self.bullet_class(
            self.game_data, self.x, self.y, angle=lead_angle, speed=bullet_speed,
            rad=max(self.rad / 5, ENEMY_BULLET_RAD),
            color=self.color, dmg=self.dmg, hp=self.hp / 10
        ))

class ShieldedEnemy(Enemy):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 radius=10, speed=PLAYER_SPEED, hp=10, shield_hp=None, shield_rad=None, **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, radius=radius, speed=speed, hp=hp, **kwargs)
        self.shoot_timer = 0
        shield_rad = shield_rad if shield_rad is not None else max(50, self.rad + 2 * hp)
        shield_hp = shield_hp if shield_hp is not None else 2 * hp
        self.parent_list.append(Shield(game_data, x, y, shield_rad, color=self.color,
                                       hp=shield_hp, parent=self, regen_rate=shield_hp / 100))

class SpawningEnemy(Enemy):
    def __init__(self, game_data: GameData, x, y, targets: list[GameParticle], parent_list: list[GameParticle],
                 child_class: type=Enemy, child_kwargs: Optional[dict]=None,
                 child_speed: tuple[float, float] = (PLAYER_SPEED, PLAYER_SPEED * 2), **kwargs):
        super().__init__(game_data, x, y, targets, parent_list, **kwargs)
        self.child_class = child_class
        self.child_kwargs = {} if child_kwargs is None else child_kwargs
        self.child_speed = child_speed
        self.child_count = 0

    def move(self):
        super().move()
        self.spawn_with_cd()

    def spawn_with_cd(self):
        max_cap = (self.hp / self.max_hp) * (self.score / 1000)
        spawn_cd = 1000  # (1000 * self.max_hp / self.hp)

        if self.child_count + max_cap / spawn_cd < max_cap:
            self.child_count += max_cap / spawn_cd
        # max_cap - 1: only spawn when is hit (hp decrease)
        # max_cap: can spawn naturally
        if self.child_count < max_cap - 1:
            return
        if self.distance_with(self.target) > self.shoot_range:
            return
        self.spawn_childs(int(self.child_count))
        self.child_count = 0

    def spawn_childs(self, total: int, **kwargs):
        total = min(MAX_ENEMY_COUNT - len(self.parent_list), total)
        for i in range(int(total)):
            angle = i / total * math.pi * 2
            x = self.x + math.cos(angle) * (UNIT_RADIUS * 3 * (i % 3) + self.rad)
            y = self.y + math.sin(angle) * (UNIT_RADIUS * 3 * (i % 3) + self.rad)
            child = self.child_class(self.game_data, x, y, self.target_list, self.parent_list,
                                     speed=random.uniform(self.child_speed[0], self.child_speed[1]),
                                     angle=angle,
                                     color=self.color,
                                     **kwargs, **self.child_kwargs)
            child.angle = angle
            child.move()
            self.parent_list.append(child)

    def on_death(self):
        self.spawn_childs(self.child_count)
        return super().on_death()

class EliteEnemy(ShootingEnemy, DodgingEnemy, ShieldedEnemy):
    pass

class EnemyMothership(SpawningEnemy, ShieldedEnemy, ShootingEnemy):
    pass
