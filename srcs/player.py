import math
import pygame
import utils
from constants import *


class Player:
    def __init__(self, x, y, rad=PLAYER_RADIUS):
        self.x = x
        self.y = y
        self.xv = 0
        self.yv = 0
        self.rad = rad

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, PLAYER_COLOR, (self.x, self.y), self.rad)

    def move(self):
        self.x += self.xv
        self.y += self.yv
        self.x = utils.normalize(self.x, self.rad, MAP_WIDTH - self.rad)
        self.y = utils.normalize(self.y, self.rad, MAP_HEIGHT - self.rad)

    def set_velocity(self, dx, dy):
        self.xv = dx
        self.yv = dy

    def recoil(self, shooting_angle, magnitude):
        self.x -= math.cos(shooting_angle) * magnitude
        self.y -= math.sin(shooting_angle) * magnitude
