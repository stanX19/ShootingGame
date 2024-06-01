# Enemy class
import pygame
import math
import utils
from constants import *


class Enemy:
    def __init__(self, x, y, radius=ENEMY_RADIUS, speed=ENEMY_SPEED, color=ENEMY_COLOR, hp=1, score=100,
                 variable_shape=False):
        self.x = x
        self.y = y
        self.xv = 0
        self.yv = 0
        self.rad = radius
        self.color = color
        self.hp = hp
        self.score = score
        self.speed = speed
        self.variable_shape = variable_shape

        if variable_shape:
            self.update_appearance_based_on_hp()

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.rad)

    def move_towards_player(self, player):
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.xv = self.speed * math.cos(angle)
        self.yv = self.speed * math.sin(angle)
        self.x += self.xv
        self.y += self.yv

        if self.variable_shape:
            self.update_appearance_based_on_hp()

    def update_appearance_based_on_hp(self):
        self.rad = Enemy.get_rad(self.hp)
        self.color = Enemy.get_color(self.hp, self.speed)

    @staticmethod
    def get_rad(hp):
        return ENEMY_RADIUS + hp - 1

    @staticmethod
    def get_color(hp, speed):
        return utils.color_norm((255, 105 - hp, 80 - hp + speed * 50))
