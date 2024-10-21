from __future__ import annotations
import math
from typing import Optional

import pygame
from srcs import utils
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.weapon_handler import WeaponHandler
from srcs.classes.game_data import GameData


class Player(GameParticle):
    def __init__(self, game_data: GameData, x: float, y: float, rad=PLAYER_RADIUS):
        super().__init__(x, y, radius=rad, color=PLAYER_COLOR, hp=PLAYER_HP)
        self.game_data: GameData = game_data
        self.main_weapon: Optional[WeaponHandler] = WeaponHandler(game_data)
        self.sub_weapon: Optional[WeaponHandler] = WeaponHandler(game_data)

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
        self.xv -= math.cos(shooting_angle) * magnitude
        self.yv -= math.sin(shooting_angle) * magnitude
