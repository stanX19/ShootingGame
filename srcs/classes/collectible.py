from __future__ import annotations

import random
import copy
import pygame
from srcs.classes.game_particle import GameParticle
from srcs.classes.weapons import MainWeaponEnum, SubWeaponEnum, WeaponType
from srcs.constants import *
from srcs.classes import draw_utils


class Collectible(GameParticle):
    def __init__(self, x, y, game, color=(125, 125, 125), radius=COLLECTIBLE_RADIUS):
        super().__init__(x, y, dmg=0, hp=1, color=color, radius=radius)
        self.game = game

    def move(self):
        pass

    def on_collect(self):
        pass


class HealCollectible(Collectible):
    def on_collect(self):
        self.game.player.hp = min(PLAYER_HP, self.game.player.hp + HEAL_HP)

    def draw(self, surface: pygame.Surface):
        COLOR1 = (0, 255, 0)
        COLOR2 = (0, 155, 0)
        draw_utils.draw_cross(surface, self.x, self.y, self.rad, COLOR1, COLOR2)


class WeaponCollectible(Collectible):
    def __init__(self, x, y, game):
        super(WeaponCollectible, self).__init__(x, y, game)
        self.weapon = random.choice(
            [attr for attr in vars(MainWeaponEnum).values() if isinstance(attr, WeaponType)]
        )

        # h1 = self.rad  # height of vertical and horizontal edge
        # h2 = self.rad // 2  # height of diagonal edge
        # w1 = h1 // 10  # width of vertical edge
        # w2 = h2 // 4  # width of diagonal edge
        #
        # # comment follows cartesian
        # self.draw_points = [
        #     (self.x, self.y + h1),  # Top
        #     (self.x + w1, self.y + w1 + w2),
        #     (self.x + h2, self.y + h2),
        #     (self.x + w1 + w2, self.y + w1),
        #     (self.x + h1, self.y),  # Right
        #     (self.x + w1 + w2, self.y - w1),
        #     (self.x + h2, self.y - h2),
        #     (self.x + w1, self.y - w1 - w2),
        #     (self.x, self.y - h1),  # Bot
        #     (self.x - w1, self.y - w1 - w2),
        #     (self.x - h2, self.y - h2),
        #     (self.x - w1 - w2, self.y - w1),
        #     (self.x - h1, self.y),  # Left
        #     (self.x - w1 - w2, self.y + w1),
        #     (self.x - h2, self.y + h2),
        #     (self.x - w1, self.y + w1 + w2),
        # ]

    def on_collect(self):
        self.game.main_weapon.change_weapon(self.weapon)

    def draw(self, surface: pygame.Surface):
        COLOR1 = (25, 255, 255)
        COLOR2 = (0, 0, 255)
        draw_utils.draw_star(surface, self.x, self.y, self.rad, COLOR1, COLOR2)
        # pygame.draw.circle(surface, COLOR2, (self.x, self.y), radius=self.rad // 2)
        # pygame.draw.polygon(surface, COLOR1, self.draw_points)


class WeaponUpgradeCollectible(Collectible):
    def on_collect(self):
        self.game.main_weapon.upgrade_weapon()

    def draw(self, surface: pygame.Surface):
        COLOR1 = (255, 155, 0)
        COLOR2 = (255, 255, 0)
        draw_utils.draw_arrow(surface, self.x, self.y, self.rad, COLOR1, COLOR2)
        # w = self.rad
        # h = self.rad
        # pygame.draw.polygon(surface, COLOR1, (
        #     (self.x, self.y - h),        # Top point
        #     (self.x - w, self.y),        # Bottom-left point
        #     (self.x - w // 2, self.y),        # Left inner point
        #     (self.x - w // 2, self.y + h), # Left inner bottom point
        #     (self.x + w // 2, self.y + h), # Right inner bottom point
        #     (self.x + w // 2, self.y),        # Right inner point
        #     (self.x + w, self.y)         # Bottom-right point
        # ))
        # w -= 3
        # h -= 3
        # pygame.draw.polygon(surface, COLOR2, (
        #     (self.x, self.y - h),  # Top point
        #     (self.x - w, self.y),  # Bottom-left point
        #     (self.x - w // 2, self.y),  # Left inner point
        #     (self.x - w // 2, self.y + h),  # Left inner bottom point
        #     (self.x + w // 2, self.y + h),  # Right inner bottom point
        #     (self.x + w // 2, self.y),  # Right inner point
        #     (self.x + w, self.y)  # Bottom-right point
        # ))
