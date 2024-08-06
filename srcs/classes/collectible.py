from __future__ import annotations

import random
import copy
import pygame
from srcs.classes.game_particle import GameParticle
from srcs.classes.weapons import MainWeaponEnum, SubWeaponEnum, WeaponType
from srcs.constants import *
from srcs.classes import draw_utils


MAIN_WEAPON_THEME = ((255, 255, 0), (255, 155, 0))
SUB_WEAPON_THEME = ((25, 255, 255), (0, 0, 255))


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
        draw_utils.draw_cross(surface, self.x, self.y, self.rad * 3 // 4, COLOR1, COLOR2)


class WeaponCollectible(Collectible):
    def __init__(self, x, y, game):
        super(WeaponCollectible, self).__init__(x, y, game)
        self.weapon = random.choice(
            [attr for attr in vars(MainWeaponEnum).values() if isinstance(attr, WeaponType)]
        )

    def on_collect(self):
        self.game.main_weapon.change_weapon(self.weapon)

    def draw(self, surface: pygame.Surface):
        draw_utils.draw_star(surface, self.x, self.y, self.rad, *MAIN_WEAPON_THEME)


class SubWeaponCollectible(Collectible):
    def __init__(self, x, y, game):
        super().__init__(x, y, game)
        self.weapon = random.choice(
            [attr for attr in vars(SubWeaponEnum).values() if isinstance(attr, WeaponType)]
        )

    def on_collect(self):
        self.game.sub_weapon.change_weapon(self.weapon)

    def draw(self, surface: pygame.Surface):
        draw_utils.draw_star(surface, self.x, self.y, self.rad, *SUB_WEAPON_THEME)


class WeaponUpgradeCollectible(Collectible):
    def on_collect(self):
        self.game.main_weapon.upgrade_weapon()

    def draw(self, surface: pygame.Surface):
        draw_utils.draw_arrow(surface, self.x, self.y, self.rad, *MAIN_WEAPON_THEME)


class SubWeaponUpgradeCollectible(Collectible):
    def on_collect(self):
        self.game.sub_weapon.upgrade_weapon()

    def draw(self, surface: pygame.Surface):
        draw_utils.draw_arrow(surface, self.x, self.y, self.rad, *SUB_WEAPON_THEME)
