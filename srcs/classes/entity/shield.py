from __future__ import annotations
from typing import Optional

import pygame

from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.entity.game_particle import GameParticle, Particle
from srcs.classes.faction_data import FactionData
from srcs import utils


class Shield(FactionParticle):
    default_color = (0, 255, 255)

    def __init__(self, faction: FactionData, x: float=0.0, y: float=0.0, angle: float=0.0, rad=100,
                 color=default_color, hp=100, dmg=1.0,
                 parent: Optional[GameParticle] = None,
                 regen_rate: float=0.25, **kwargs):
        super().__init__(faction, x, y, angle, 0, rad, color, hp, dmg, parent=parent,
                         regen_rate=regen_rate, **kwargs)
        self._default_regen_rate = regen_rate
        self.prev_hp = self.hp
        self.is_hit = False
        self.show_timer = 0
        self.width = 3
        self.show_duration = 30
        self.tick = 0
        self.down_cd = 180
        self.down_timer = 0
        self.inner_rad = self.parent.max_rad + 20

    def move(self):
        if self.max_hp <= 0:
            return
        self.hp = utils.clamp(self.hp, 0, self.max_hp)
        self.is_hit = self.hp < self.prev_hp
        self.show_timer = self.show_duration if self.is_hit else self.show_timer

        # need to happen before prev_hp and down_timer is overwritten
        if self.down_timer > 0:
            self.rad = 0
        else:
            self.inner_rad = self.parent.max_rad + 20
            self.rad = self.inner_rad + (self.max_rad - self.inner_rad) * (self.prev_hp / self.max_hp)

        if self.hp <= 0 and self.down_timer <= 0:
            self.down_timer = self.down_cd
        else:
            self.down_timer -= 1

        self.regen_rate = self._default_regen_rate if self.show_timer <= 0 else self._default_regen_rate / 10
        self.prev_hp = self.hp

        if isinstance(self.parent, Particle):
            self.x = self.parent.x + self.parent.xv
            self.y = self.parent.y + self.parent.yv
        super().move()

    def draw(self, surface: pygame.Surface):
        if self.rad <= 0:
            return
        self.tick = (self.tick + self.is_hit) % 3
        if not self.is_hit:
            self.tick = 2
        if self.show_timer <= 0:
            return
        if self.tick < 1:
            color = utils.color_intensity_shift(self.color, 0.5 * self.show_timer / self.show_duration)
        else:
            color = utils.color_intensity_shift(self.color, 2 * self.show_timer / self.show_duration)
        pygame.draw.circle(surface,
                           color, (int(self.x), int(self.y)),
                           self.rad - self.width, width=self.width)
        self.show_timer -= 1

    def is_dead(self):
        if isinstance(self.parent, GameParticle):
            return self.parent.is_dead()
        else:
            return super().is_dead()