from __future__ import annotations
import math
import random

import pygame
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.game_data import GameData



class Effect(GameParticle):
    def __init__(self, game_data: GameData, x, y, angle, speed=0, rad=1,
                 color=(255, 255, 255), hp=1.0, dmg=1.0, lifespan=None,
                 fade_off=False):
        super().__init__(x, y, angle, speed, rad, color, hp, dmg)
        if isinstance(lifespan, tuple) and len(lifespan) > 1:
            self.lifespan = random.randint(lifespan[0], lifespan[1])
        else:
            self.lifespan = lifespan
        self.game_data: GameData = game_data
        self.fade_off = fade_off
        self.opacity = 1.0

    def apply_fade_off(self):
        self.rad *= 1.25
        self.opacity *= 0.9

    def move(self):
        super().move()
        self.lifespan -= 1
        self.apply_fade_off()

    def draw(self, surface: pygame.Surface):
        if self.opacity < 0.25 or not self.game_data.in_screen(self):
            return
        temp_surface = pygame.Surface((self.rad * 2, self.rad * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, self.color, (self.rad, self.rad), self.rad)
        temp_surface.set_alpha(int(self.opacity * 255))
        surface.blit(temp_surface, (self.x - self.rad, self.y - self.rad))

    def is_dead(self):
        return super().is_dead() or self.x < 0 or self.x > MAP_WIDTH or\
            self.y < 0 or self.y > MAP_HEIGHT or self.lifespan <= 0
