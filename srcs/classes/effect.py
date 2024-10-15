from __future__ import annotations
import math
import random

import pygame
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.game_data import GameData


DEATH_OPACITY = 0.25


class Effect(GameParticle):
    def __init__(self, game_data: GameData, x, y, angle, speed=0, rad=1,
                 color=(255, 255, 255), hp=1.0, dmg=1.0, lifespan=None,
                 fade_off=False, max_rad=None):
        super().__init__(x, y, angle, speed, rad, color, hp, dmg)
        if isinstance(lifespan, tuple) and len(lifespan) > 1:
            self.lifespan = random.randint(lifespan[0], lifespan[1])
        elif isinstance(lifespan, int):
            self.lifespan = lifespan
        else:
            self.lifespan = 60 * 2
        self.game_data: GameData = game_data
        self.fade_off = fade_off
        self.opacity = 1.0
        self.max_rad = max_rad if max_rad else rad * 2

        # Calculate the expansion rate and fade-off rate
        self.rad_increase_rate = (self.max_rad - self.rad) / self.lifespan
        self.opacity_decrease_rate = (1.0 - DEATH_OPACITY) / self.lifespan

    def apply_fade_off(self):
        self.rad += self.rad_increase_rate
        self.opacity -= self.opacity_decrease_rate

    def move(self):
        super().move()
        self.lifespan -= 1
        self.apply_fade_off()

    def draw(self, surface: pygame.Surface):
        if self.is_dead() or not self.game_data.in_screen(self):
            return
        temp_surface = pygame.Surface((self.rad * 2, self.rad * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, self.color, (self.rad, self.rad), self.rad)
        temp_surface.set_alpha(int(self.opacity * 255))
        surface.blit(temp_surface, (self.x - self.rad, self.y - self.rad))

    def is_dead(self):
        return super().is_dead() or self.x < 0 or self.x > MAP_WIDTH or\
            self.y < 0 or self.y > MAP_HEIGHT or self.lifespan <= 0 or\
            (self.max_rad and self.rad > self.max_rad) or self.opacity < DEATH_OPACITY
