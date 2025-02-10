from __future__ import annotations

import math

import pygame


class Particle:
    def __init__(self, x: float, y: float, angle=0.0, speed=0.0, rad=1.0, color=(255, 255, 255), *wargs, **kwargs):
        self.prev_x = x
        self.prev_y = y
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
            return float('inf')
        return math.hypot(self.x - other.x, self.y - other.y) - self.rad - other.rad

    def distance_with_cord(self, x, y) -> float:
        return math.hypot(self.x - x, self.y - y) - self.rad

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.rad)

    def move(self):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += self.xv
        self.y += self.yv


class GameParticle(Particle):
    def __init__(self, x: float=0.0, y: float=0.0, angle: float=0.0, speed=0.0, radius=1.0, color=(255, 255, 255), hp=1, dmg=1,
                 score=0, parent: GameParticle | None = None, regen_rate: float=0):
        super().__init__(x, y, angle, speed, radius, color)
        self.hp: float = hp
        self.max_hp: float = hp
        self.max_rad: float = radius
        self.dmg: float = dmg
        self.base_score: int = score
        self.score: int = 0
        self.parent: GameParticle | None = parent
        self.regen_rate = regen_rate

    def use_score(self, amount: int) -> bool:
        """

        :return: True if success, False otherwise
        """
        if amount > self.score:
            return False
        self.score -= amount
        self.base_score += amount
        return True

    def set_hp(self, hp):
        self.hp = min(self.max_hp, hp)

    def increase_max_hp(self, amount):
        self.hp += amount
        self.max_hp += amount

    def add_score(self, amount):
        self.score += amount
        if isinstance(self.parent, GameParticle):
            self.parent.add_score(amount)

    def get_greatest_parent(self) -> GameParticle:
        current: GameParticle = self
        while isinstance(current.parent, GameParticle):
            current = current.parent
        return current

    def regen_hp(self, regen_amount: float):
        self.hp = min(self.hp + regen_amount, self.max_hp)

    def on_death(self, *args, **kwargs) -> None:
        return

    def is_dead(self) -> bool:
        return self.hp <= 0.0

    def angle_with(self, other: Particle) -> float:
        try:
            return self.angle_with_cord(other.x, other.y)
        except AttributeError:
            return 0.0

    def angle_with_cord(self, x, y):
        y_dis = y - self.y
        x_dis = x - self.x
        return math.atan2(y_dis, x_dis)

    def move(self):
        super().move()
        self.hp = min(self.max_hp, self.hp + self.regen_rate)

    def __repr__(self):
        return f"{type(self).__name__}<{self.hp:.0f}/{self.max_hp:.0f}>"