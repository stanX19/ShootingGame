from __future__ import annotations
import math
import pygame
from srcs import utils
from srcs.constants import *
from srcs.classes.game_particle import GameParticle


class Player(GameParticle):
    def __init__(self, x: float, y: float, rad=PLAYER_RADIUS):
        super().__init__(x, y, radius=rad, color=PLAYER_COLOR, hp=PLAYER_HP)

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, PLAYER_COLOR, (self.x, self.y), self.rad)

    def move(self):
        super().move()
        self.x = utils.normalize(self.x, self.rad, MAP_WIDTH - self.rad)
        self.y = utils.normalize(self.y, self.rad, MAP_HEIGHT - self.rad)

    def set_velocity(self, dx: float, dy: float):
        self.xv = dx
        self.yv = dy

    def get_xy(self):
        return self.x, self.y

    def recoil(self, shooting_angle: float, magnitude: float):
        self.x -= math.cos(shooting_angle) * magnitude
        self.y -= math.sin(shooting_angle) * magnitude
