from __future__ import annotations

import math
import random

import pygame

from srcs import utils
from srcs.classes.effect import Effect
from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.entity.lazer import Lazer
from srcs.classes.faction_data import FactionData
from srcs.classes.game_data import GameData
from srcs.constants import *
from srcs.utils import color_mix


class Debris(Effect):
    def __init__(self, game_data: GameData, x, y, angle, speed=0, rad=5.0,  # Increased default rad for visibility
                 color=(255, 255, 255), hp=1.0, dmg=1.0, **kwargs):
        super().__init__(game_data, x, y, angle, speed, rad, color, hp, dmg,
                         lifespan=300, target_rad=0.5, fade_off=True, **kwargs)
        self.orientation_angle = random.uniform(0, 2 * math.pi)  # Initial random orientation
        self.angular_momentum = random.uniform(-math.pi * 2 / FPS, math.pi * 2 / FPS)  # Random angular momentum (radians per frame)

    def move(self):
        super().move()
        self.orientation_angle += self.angular_momentum

    def draw(self, surface: pygame.Surface):
        if self.is_dead() or self.rad <= 0:
            return

        points = []
        for i in range(3):
            angle_rad = self.orientation_angle + i * 2 * math.pi / 3  # Use radians directly
            point_x = self.x + self.rad * math.cos(angle_rad)
            point_y = self.y + self.rad * math.sin(angle_rad)
            points.append((point_x, point_y))

        pygame.draw.polygon(surface, (*self.color, int(self.opacity * 255)), points)



class Breakable(FactionParticle):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0, speed=0.0, radius=1.0,
                 color=(255, 255, 255), hp=1, dmg=1,
                 score=0, **kwargs):
        super().__init__(faction, x, y, angle, speed, radius, color, hp, dmg, score, **kwargs)
        self._explode_prev_hp: float = self.hp

    def move(self):
        super().move()
        if self.hp < self._explode_prev_hp:
            self.explode()
        self._explode_prev_hp = self.hp

    def on_death(self):
        self.explode()
        return super().on_death()

    def handle_hit_by(self, other: GameParticle):
        angle = self.angle_with(other)
        rad = other.rad
        spread = math.pi / 2
        if isinstance(other, Lazer):
            rad = other.rad
            angle = utils.angle_add(other.angle_with_cord(self.x, self.y), math.pi)
        if self.hp <= 0:
            # angle = utils.angle_add(angle, math.pi)
            spread = math.pi * 2
        x = self.x + max(self.rad * 0.9, self.rad - UNIT_RADIUS) * math.cos(angle)
        y = self.y + max(self.rad * 0.9, self.rad - UNIT_RADIUS) * math.sin(angle)
        self._explode(angle, spread, (x, y), 0,
                      max(1, other.speed / max(rad, 0.1) / 1000))

    def _explode(self, explode_angle: float, explode_spread: float, spawn_center:tuple, spawn_rad:float, velocity_k:float=1.0):
        explode_hp = (self._explode_prev_hp - max(0.0, self.hp)) * 0.25
        self._explode_prev_hp = self.hp
        # n = particle count, k = maximum size
        cap = MAX_ENEMY_COUNT - len(self.faction.parent_list)
        k = 2.0
        color = color_mix(self.color, (255, 255, 255), weight2=2)
        for j in range(cap):
            if explode_hp <= 0:
                return
            particle_angle = explode_angle + random.uniform(-explode_spread / 2, explode_spread / 2)
            radius = random.uniform(0.1, min(UNIT_RADIUS * k, self.max_rad / 3))
            hp = radius / 10
            carried_hp = self.max_hp * (radius / self.rad) ** 2
            explode_hp -= carried_hp
            speed = (random.uniform(UNIT_SPEED * 2, UNIT_SPEED * (10 + j / 4)) / radius
                    * velocity_k)
            offset_x = math.cos(particle_angle) * (radius + spawn_rad)
            offset_y = math.sin(particle_angle) * (radius + spawn_rad)
            particle_x = spawn_center[0] + offset_x
            particle_y = spawn_center[1] + offset_y
            particle = Debris(self.faction.game_data, particle_x, particle_y, particle_angle, speed, radius,
                              color, hp, speed * hp, parent=self)
            particle.xv += self.xv
            particle.yv += self.yv
            self.faction.parent_list.append(particle)

    # def _explode0(self, explode_angle: float, explode_spread: float, spawn_center:tuple, spawn_rad:float, velocity_k:float=1.0):
    #     explode_hp = self._explode_prev_hp - max(0.0, self.hp)
    #     self._explode_prev_hp = self.hp
    #
    #     if explode_hp == 0:
    #         return
    #
    #     # n = particle count, k = maximum size
    #     cap = MAX_ENEMY_COUNT - len(self.faction.parent_list)
    #     k = 0.5
    #     n = min(cap, random.randint(max(3, math.ceil(explode_hp / 2)),
    #                                 max(3, math.ceil(explode_hp))))  # math.ceil(explode_hp / 2 + 1)
    #
    #     color = color_mix(self.color, (255, 255, 255), weight2=2)
    #     offset_angle = random.uniform(-explode_spread / 10, explode_spread / 10)
    #     for i in range(n):
    #         particle_angle = explode_angle + (explode_spread / n) * (i - n / 2) + offset_angle
    #
    #         radius = random.uniform(0.1, min(UNIT_RADIUS * k, self.max_rad / 3))
    #         hp = radius / 10
    #         speed = (random.uniform(UNIT_SPEED * 2, UNIT_SPEED * (2 + n / 4)) / radius * k
    #                 * velocity_k)
    #         offset_x = math.cos(particle_angle) * (radius + spawn_rad)
    #         offset_y = math.sin(particle_angle) * (radius + spawn_rad)
    #         particle_x = spawn_center[0] + offset_x
    #         particle_y = spawn_center[1] + offset_y
    #         particle = Debris(self.faction.game_data, particle_x, particle_y, particle_angle, speed, radius,
    #                           color, hp, speed * hp, parent=self)
    #         particle.xv += self.xv
    #         particle.yv += self.yv
    #         self.faction.parent_list.append(particle)

    def explode(self):
        self._explode(self.angle, math.pi * 2, (self.x, self.y), self.rad)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # draw_arrow(surface, (self.x, self.y), (self.target.x, self.target.y))
