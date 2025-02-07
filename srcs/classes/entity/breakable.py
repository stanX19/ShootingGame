from __future__ import annotations

import math
import random

import pygame

from srcs.classes.effect import Effect
from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.faction_data import FactionData
from srcs.classes.game_data import GameData
from srcs.constants import *
from srcs.utils import color_mix


class Debris(Effect):
    def __init__(self, game_data: GameData, x, y, angle, speed=0, rad=1.0,
                 color=(255, 255, 255), hp=1.0, dmg=1.0):
        super().__init__(game_data, x, y, angle, speed, rad, color, hp, dmg, lifespan=300, target_rad=0.1, fade_off=True)


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
        x = self.x + max(self.rad * 0.9, self.rad - UNIT_RADIUS) * math.cos(angle)
        y = self.y + max(self.rad * 0.9, self.rad - UNIT_RADIUS) * math.sin(angle)
        self._explode(angle, math.pi / 2, (x, y), 0)

    def _explode(self, explode_angle: float, explode_spread: float, spawn_center:tuple, spawn_rad:float):
        explode_hp = self._explode_prev_hp - self.hp
        self._explode_prev_hp = self.hp

        if explode_hp == 0:
            return

        # n = particle count, k = maximum size
        cap = MAX_ENEMY_COUNT - len(self.faction.parent_list)
        k = 0.5
        n = min(cap, random.randint(max(3, math.ceil(explode_hp / 2)),
                                    max(3, math.ceil(explode_hp))))  # math.ceil(explode_hp / 2 + 1)

        color = color_mix(self.color, (255, 255, 255), weight2=2)
        offset_angle = random.uniform(-explode_spread / 10, explode_spread / 10)
        for i in range(n):
            particle_angle = explode_angle + (explode_spread / n) * (i - n / 2) + offset_angle

            radius = random.uniform(0.1, min(UNIT_RADIUS * k, self.max_rad / 3))
            hp = radius / 10
            speed = random.uniform(UNIT_SPEED * 2, UNIT_SPEED * (2 + n / 4)) / radius * k * (self.rad / UNIT_RADIUS)

            offset_x = math.cos(particle_angle) * (radius + spawn_rad)
            offset_y = math.sin(particle_angle) * (radius + spawn_rad)
            particle_x = spawn_center[0] + offset_x
            particle_y = spawn_center[1] + offset_y
            particle = Debris(self.faction.game_data, particle_x, particle_y, particle_angle, speed, radius,
                              color, hp, speed * hp)
            particle.xv += self.xv
            particle.yv += self.yv
            self.faction.parent_list.append(particle)

    def explode(self):
        self._explode(self.angle, math.pi * 2, (self.x, self.y), self.rad)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # draw_arrow(surface, (self.x, self.y), (self.target.x, self.target.y))
