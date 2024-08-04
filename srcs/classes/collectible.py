from __future__ import annotations

import random
import pygame

from srcs.classes.game_particle import GameParticle
from srcs.constants import *


class Collectible(GameParticle):
    def __init__(self, x, y, game, color, radius=COLLECTIBLE_RADIUS):
        super().__init__(x, y, dmg=0, hp=1, color=color, radius=radius)
        self.game = game

    def move(self):
        pass

    def on_collect(self):
        pass


class HealCollectible(Collectible):
    def __init__(self, x, y, game):
        super().__init__(x, y, game, color=(0, 255, 0))

    def on_collect(self):
        self.game.player.hp = min(PLAYER_HP, self.game.player.hp + HEAL_HP)

    def draw(self, surface: pygame.Surface):
        WIDTH = self.rad * 0.75
        pygame.draw.rect(surface, self.color, (self.x - WIDTH / 2, self.y - self.rad, WIDTH, 2 * self.rad))
        pygame.draw.rect(surface, self.color, (self.x - self.rad, self.y - WIDTH / 2, 2 * self.rad, WIDTH))


class WeaponCollectible(Collectible):
    def __init__(self, x, y, game):
        super().__init__(x, y, game, color=(25, 255, 255))

    def on_collect(self):
        self.game.main_weapon.set_weapon_by_index(random.randint(0, len(self.game.main_weapon.all_weapon) - 1))

    def draw(self, surface: pygame.Surface):
        WIDTH = self.rad * 3 // 4
        pygame.draw.polygon(surface, self.color, (
            (self.x - self.rad, self.y),
            (self.x, self.y - self.rad),
            (self.x + self.rad, self.y),
            (self.x, self.y + self.rad),
        ))
        pygame.draw.rect(surface, self.color, (self.x - WIDTH, self.y - WIDTH, WIDTH * 2, WIDTH * 2))
        # pygame.draw.polygon(surface, self.color, (
        #     (self.x - self.rad, self.y),
        #     (self.x - WIDTH, self.y - WIDTH),
        #     (self.x, self.y - self.rad),
        #     (self.x + WIDTH, self.y - WIDTH),
        #     (self.x + self.rad, self.y),
        #     (self.x - WIDTH, self.y + WIDTH),
        #     (self.x, self.y + self.rad),
        #     (self.x + WIDTH, self.y + WIDTH),
        # ))
