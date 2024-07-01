import math
import pygame
from srcs.constants import *
from srcs.classes.weapons import WeaponType


# Bullet class
class WaterParticle:
    def __init__(self, x, y, angle, speed=3, rad=3, weapon=None,
                hp=1, dmg=0, lifespan=60 * 4):
        self.x = x
        self.y = y
        if isinstance(weapon, WeaponType):
            if speed == 3:
                speed = weapon.speed
            if rad == 3:
                rad = weapon.rad
            if hp == 1:
                hp = weapon.hp
            if dmg == 1:
                dmg = weapon.dmg
        if speed is None:
            speed = 10
        self.xv = speed * math.cos(angle)
        self.yv = speed * math.sin(angle)
        self.rad = rad
        self.collide_rad = rad / 5
        self.hp = hp
        self.dmg = dmg
        self.lifespan = lifespan
        self.mass = 10

    @property
    def speed(self):
        return math.hypot(self.xv, self.yv)

    @speed.setter
    def speed(self, new_speed):
        angle = self.angle
        self.xv = new_speed * math.cos(angle)
        self.yv = new_speed * math.sin(angle)

    @property
    def angle(self):
        return math.atan2(self.yv, self.xv)

    @angle.setter
    def angle(self, new_angle):
        speed = self.speed
        self.xv = speed * math.cos(new_angle)
        self.yv = speed * math.sin(new_angle)

    def move(self):
        self.lifespan -= 1
        self.x += self.xv
        self.y += self.yv
        self.dmg = self.speed / 5

    def distance_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)
