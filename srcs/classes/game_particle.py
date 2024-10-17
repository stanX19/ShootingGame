from __future__ import annotations

import math

import pygame


class Particle:
    def __init__(self, x: float, y: float, angle=0.0, speed=0.0, rad=1.0, color=(255, 255, 255), *wargs, **kwargs):
        self.x: float = x
        self.y: float = y
        self.xv: float = speed * math.cos(angle)
        self.yv: float = speed * math.sin(angle)
        self.rad: float = rad
        self.color: tuple[int, int, int] = color

    @property
    def speed(self):
        return math.hypot(self.xv, self.yv)

    @speed.setter
    def speed(self, new_speed: float):
        angle = self.angle
        self.xv = new_speed * math.cos(angle)
        self.yv = new_speed * math.sin(angle)

    @property
    def angle(self):
        return math.atan2(self.yv, self.xv)

    @angle.setter
    def angle(self, new_angle: float):
        speed = self.speed
        self.xv = speed * math.cos(new_angle)
        self.yv = speed * math.sin(new_angle)

    def distance_with(self, other) -> float:
        if other is None:
            return 0
        return math.hypot(self.x - other.x, self.y - other.y)

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.rad)

    def move(self):
        self.x += self.xv
        self.y += self.yv


class GameParticle(Particle):
    def __init__(self, x: float, y: float, angle=0.0, speed=0.0, radius=1.0, color=(255, 255, 255), hp=1, dmg=1,
                 score=0):
        super().__init__(x, y, angle, speed, radius, color)
        self.hp: float = hp
        self.max_hp: float = hp
        self.dmg: float = dmg
        self.score: int = score

    def on_death(self, *args, **kwargs) -> None:
        return

    def is_dead(self) -> bool:
        return self.hp <= 0.0

    def angle_with(self, other: Particle) -> float:
        try:
            y_dis = other.y - self.y
            x_dis = other.x - self.x
            return math.atan2(y_dis, x_dis)
        except AttributeError:
            return 0.0
