from __future__ import annotations

import math
import random

import pygame

from srcs.classes.effect import Effect
from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.faction_data import FactionData
from srcs.constants import *
from srcs.utils import color_mix


class Breakable(FactionParticle):
    def __init__(self, faction: FactionData, x: float, y: float, angle=0.0, speed=0.0, radius=1.0,
                 color=(255, 255, 255), hp=1, dmg=1,
                 score=0, **kwargs):
        super().__init__(faction, x, y, angle, speed, radius, color, hp, dmg, score, **kwargs)

    def on_death(self):
        self.explode()
        return super().on_death()

    def explode(self):
        # n = particle count
        k = 0.75
        n = random.randint(max(3, math.ceil(self.max_hp / 2)),
                           max(3, math.ceil(self.max_hp)))  # math.ceil(self.max_hp / 2 + 1)
        particle_angle = self.angle
        color = color_mix(self.color, (255, 255, 255), weight2=2)
        for i in range(n):
            particle_angle += (2 * math.pi / n) * i

            radius = random.uniform(0.1, min(UNIT_RADIUS * k, self.max_rad / 3))
            hp = radius / 10
            speed = random.uniform(UNIT_SPEED * 2, UNIT_SPEED * (2 + n / 4)) / radius * k

            offset_x = math.cos(particle_angle) * radius
            offset_y = math.sin(particle_angle) * radius
            particle_x = self.x + offset_x
            particle_y = self.y + offset_y
            particle = Effect(self.faction.game_data, particle_x, particle_y, particle_angle, speed, radius,
                              color, hp, speed * hp,
                              lifespan=3000, target_rad=0.1, fade_off=False)
            particle.xv += self.xv
            particle.yv += self.yv
            self.faction.parent_list.append(particle)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # draw_arrow(surface, (self.x, self.y), (self.target.x, self.target.y))
