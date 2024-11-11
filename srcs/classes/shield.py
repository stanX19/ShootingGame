from __future__ import annotations
import random
from typing import Optional

import pygame
from matplotlib.style.core import available

from srcs.constants import *
from srcs.classes.weapons import WeaponType
from srcs.classes.game_particle import GameParticle
from srcs.classes.game_data import GameData
from srcs import utils


class Shield(GameParticle):
    def __init__(self, game_data: GameData, x, y, rad=100,
                 color=(0, 255, 255), hp=1.0, dmg=1.0,
                 parent: Optional[GameParticle] = None,
                 regen_rate: float=1):
        super().__init__(x, y, 0, 0, rad, color, hp, dmg)
        self.game_data: GameData = game_data
        self.parent: Optional[GameParticle] = parent
        self.prev_hp = self.hp
        self.is_hit = False
        self.show_timer = 0
        self.width = 3
        self.show_duration = 60
        self.tick = 0
        self.regen_rate = regen_rate
        self.down_cd = 20
        self.down_timer = 0

    def move(self):
        super().move()
        self.is_hit = self.hp < self.prev_hp
        if self.hp <= 0 and self.down_timer <= 0:
            self.down_timer = self.down_cd
        else:
            self.down_timer -= 1
        self.hp = min(self.hp + self.regen_rate * (self.down_timer <= 0), self.max_hp)
        self.prev_hp = self.hp

        if self.parent is not None:
            self.x = self.parent.x
            self.y = self.parent.y
            # missing_hp = self.parent.max_hp - self.parent.hp
            # transferred_hp = min(self.hp, missing_hp)
            # self.hp -= transferred_hp
            # self.parent.hp += transferred_hp

    def draw(self, surface: pygame.Surface):
        if super().is_dead():
            return
        self.show_timer = self.show_duration if self.is_hit else self.show_timer
        self.tick = (self.tick + self.is_hit) % 3
        if not self.is_hit:
            self.tick = 2
        if self.show_timer > 0:
            if self.tick < 1:
                color = utils.color_intensity_shift(self.color, 0.5 * self.show_timer / self.show_duration)
            else:
                color = utils.color_intensity_shift(self.color, 2 * self.show_timer / self.show_duration)
            pygame.draw.circle(surface,
                               color, (int(self.x), int(self.y)),
                               self.rad - self.width, width=self.width)
            self.show_timer -= 1

    def parent_is_dead(self):
        return self.parent is None or self.parent.is_dead()

    def is_dead(self):
        return super().is_dead() and self.parent_is_dead()