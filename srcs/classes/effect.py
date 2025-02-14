from __future__ import annotations
import random
from multiprocessing.managers import Value

import pygame
from srcs.constants import *
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.game_data import GameData


DEATH_OPACITY = 0.025


class Effect(GameParticle):
    def __init__(self, game_data: GameData, x, y, angle, speed=0, rad=1,
                 color=(255, 255, 255), hp=1.0, dmg=1.0, lifespan=None,
                 fade_off=False, fade_in=False, target_rad=None, **kwargs):
        super().__init__(x, y, angle, speed, rad, color, hp, dmg, **kwargs)

        if fade_off and fade_in:
            raise ValueError("Cannot fade in and fade out at the same time")

        self.lifespan = lifespan if lifespan is not None else 60 * 2
        self.game_data: GameData = game_data
        self.fade = fade_off or fade_in
        self.target_rad = target_rad if target_rad is not None else rad * 2

        # Calculate the expansion rate and fade-off rate
        self.rad_increase_rate = (self.target_rad - self.rad) / self.lifespan

        # fade off rate
        self.opacity = 1.0
        self.opacity_increase_rate = (DEATH_OPACITY - self.opacity) / self.lifespan
        if fade_in:
            self.opacity = DEATH_OPACITY + 0.01
            self.opacity_increase_rate = (1.0 - self.opacity) / self.lifespan

    def apply_fade(self):
        self.opacity += self.opacity_increase_rate

    def move(self):
        super().move()
        self.lifespan -= 1
        self.rad += self.rad_increase_rate
        if self.fade:
            self.apply_fade()

    def draw(self, surface: pygame.Surface):
        if self.is_dead() or self.rad <= 0:
            return
        temp_surface = pygame.Surface((self.rad * 2, self.rad * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, self.color, (self.rad, self.rad), self.rad)
        temp_surface.set_alpha(int(self.opacity * 255))
        surface.blit(temp_surface, (self.x - self.rad, self.y - self.rad))

    def is_dead(self):
        return super().is_dead() or self.x + self.rad < 0 or self.x - self.rad > MAP_WIDTH or\
            self.y + self.rad < 0 or self.y - self.rad > MAP_HEIGHT or self.lifespan <= 0
