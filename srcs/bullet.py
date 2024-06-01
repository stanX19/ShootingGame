import math
import pygame
from constants import *
from weapons import WeaponType


# Bullet class
class Bullet:
    def __init__(self, x, y, angle, speed=None, rad=None, weapon=None, hp=1, dmg=1, lifespan=60 * 4):
        self.x = x
        self.y = y
        if isinstance(weapon, WeaponType):
            if speed is None:
                speed = weapon.speed
            if rad is None:
                rad = weapon.rad
            if hp == 1:
                hp = weapon.hp
            if dmg == 1:
                dmg = weapon.dmg
        self.xv = speed * math.cos(angle)
        self.yv = speed * math.sin(angle)
        self.speed = speed
        self.rad = rad
        self.hp = hp
        self.dmg = dmg
        self.lifespan = lifespan

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), self.rad)

    def move(self):
        self.lifespan -= 1
        self.x += self.xv
        self.y += self.yv

