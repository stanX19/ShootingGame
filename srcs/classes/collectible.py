from __future__ import annotations

import random
import pygame
from srcs.classes.game_particle import GameParticle
from srcs.classes.weapons import ALL_SUB_WEAPON_LIST, ALL_MAIN_WEAPON_LIST
from srcs.classes.weapon_handler import WeaponHandler
from srcs import constants
from srcs.classes import draw_utils
from srcs.classes.game_data import GameData


MAIN_WEAPON_THEME = ((255, 255, 0), (255, 155, 0))
SUB_WEAPON_THEME = ((25, 255, 255), (0, 0, 255))


class Collectible(GameParticle):
    def __init__(self, x, y, game_data: GameData, color=(125, 125, 125), radius=constants.COLLECTIBLE_RADIUS):
        super().__init__(x, y, dmg=0, hp=1, color=color, radius=radius)
        self.game_data: GameData = game_data

    def move(self):
        pass

    def on_collect(self):
        pass


class HealCollectible(Collectible):
    def on_collect(self):
        self.game_data.player.max_hp += constants.HEAL_HP  #  max(self.data.player.max_hp, self.data.player.hp + constants.HEAL_HP)
        self.game_data.player.hp = min(self.game_data.player.max_hp, self.game_data.player.hp + constants.HEAL_HP)

    def draw(self, surface: pygame.Surface):
        COLOR1 = (0, 255, 0)
        COLOR2 = (0, 155, 0)
        draw_utils.draw_cross(surface, self.x, self.y, self.rad * 3 // 4, COLOR1, COLOR2)


class MainWeaponCollectible(Collectible):
    def __init__(self, x, y, game):
        super().__init__(x, y, game)
        self.weapon_handler: WeaponHandler = game.main_weapon

    def _get_not_collected(self):
        collected_names = [i.name for i in self.game_data.player.main_weapon.all_weapon]
        not_collected = [i for i in ALL_MAIN_WEAPON_LIST if i.name not in collected_names]
        return not_collected

    def on_collect(self):
        not_collected = self._get_not_collected()
        if not not_collected:
            return
        weapon = random.choice(not_collected)
        self.weapon_handler.change_weapon(weapon)

    def draw(self, surface: pygame.Surface):
        draw_utils.draw_star(surface, self.x, self.y, self.rad, *MAIN_WEAPON_THEME)

    def is_dead(self):
        return super().is_dead() or not self._get_not_collected()


class SubWeaponCollectible(MainWeaponCollectible):
    def __init__(self, x, y, game):
        super().__init__(x, y, game)
        self.weapon_handler: WeaponHandler = game.sub_weapon

    def _get_not_collected(self):
        collected_names = [i.name for i in self.game_data.player.sub_weapon.all_weapon]
        not_collected = [i for i in ALL_SUB_WEAPON_LIST if i.name not in collected_names]
        return not_collected

    def draw(self, surface: pygame.Surface):
        draw_utils.draw_star(surface, self.x, self.y, self.rad, *SUB_WEAPON_THEME)


class WeaponUpgradeCollectible(Collectible):
    def on_collect(self):
        self.game_data.player.main_weapon.upgrade_weapon()

    def draw(self, surface: pygame.Surface):
        draw_utils.draw_arrow(surface, self.x, self.y, self.rad, *MAIN_WEAPON_THEME)


class SubWeaponUpgradeCollectible(Collectible):
    def on_collect(self):
        self.game_data.player.sub_weapon.upgrade_weapon()

    def draw(self, surface: pygame.Surface):
        draw_utils.draw_arrow(surface, self.x, self.y, self.rad, *SUB_WEAPON_THEME)
