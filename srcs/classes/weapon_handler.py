from __future__ import annotations
import math
import random
import copy
from srcs import constants
from srcs import utils
from srcs.classes.bullet import Bullet
from srcs.classes.missile import Missile
from srcs.classes.weapons import *


class WeaponHandler:
    def __init__(self, game, weapons: [None, list[WeaponType], type] = None):
        if isinstance(weapons, list):
            weapons = [copy.copy(weapon) for weapon in weapons if isinstance(weapon, WeaponType)]
        elif isinstance(weapons, WeaponType):
            weapons = [weapons]
        elif isinstance(weapons, type):
            weapons = [copy.copy(attr) for attr in vars(weapons).values() if isinstance(attr, WeaponType)]
        else:
            weapons = []

        self.weapon: [WeaponType, None] = weapons[0] if weapons else None
        self.all_weapon = weapons
        self.last_shot_time = {}
        self.weapon_change_energy = 10000
        self.last_reload_time = 0
        self.game = game
        self.mx, self.my = 0, 0
        self.dy, self.dx = 0, 0
        self.hypot = 0.0
        self.angle = 0.0
        self.bullet_count = 1
        self._overdrive_end_time = -constants.OVERDRIVE_CD
        self._overdrive_start_time = -constants.OVERDRIVE_CD
        self.overdrive_weapon = None

    @property
    def current_time(self):
        return self.game.current_time

    @property
    def player(self):
        return self.game.player

    @property
    def bullets_list(self):
        return self.game.bullets

    @property
    def score(self):
        return self.game.score

    @property
    def index(self):
        try:
            return self.all_weapon.index(self.weapon)
        except ValueError:
            return -1

    @property
    def name(self):
        try:
            return self.weapon.name
        except AttributeError:
            return "None"

    @property
    def overdrive_cd(self):
        return max(0.0, constants.OVERDRIVE_CD - (self.current_time - self._overdrive_end_time))

    @overdrive_cd.setter
    def overdrive_cd(self, val):
        if val < 0.0:
            return
        self._overdrive_end_time = self.current_time - constants.OVERDRIVE_CD + val

    def overdrive_start(self):
        if self.overdrive_weapon:
            return
        if self.overdrive_cd:
            return
        self._overdrive_start_time = self.current_time
        self._overdrive_end_time = self.current_time
        self.overdrive_weapon = self.weapon
        self.last_shot_time[self.overdrive_weapon] = -self.weapon.shot_delay
        self.overdrive_weapon.rad *= 2
        self.overdrive_weapon.dmg *= 5
        self.overdrive_weapon.hp *= 5
        self.overdrive_weapon.shot_delay /= 10
        constants.MAX_PARTICLE_COUNT *= 2
        # self.overdrive_weapon.speed *= 2

    def overdrive_end(self):
        if not self.overdrive_weapon:
            return
        self.overdrive_weapon.rad /= 2
        self.overdrive_weapon.dmg /= 5
        self.overdrive_weapon.hp /= 5
        self.overdrive_weapon.shot_delay *= 10
        constants.MAX_PARTICLE_COUNT /= 2
        # self.overdrive_weapon.speed /= 2
        self.overdrive_weapon = None

    def upgrade_weapon(self):
        self.weapon.level += 1

    def _set_weapon(self, weapon: WeaponType):
        if self.weapon.name == weapon.name:
            return
        if self._change_in_cooldown():
            return
        if weapon.name in [w.name for w in self.all_weapon]:
            weapon = [w for w in self.all_weapon if w.name == weapon.name][0]
        else:
            weapon = copy.copy(weapon)
            self.all_weapon.append(weapon)
        self.on_mouse_up()
        self.overdrive_end()
        self.weapon = weapon

    def cycle_weapon(self):
        idx = (self.index + 1) % len(self.all_weapon)
        self._set_weapon(self.all_weapon[idx])

    def set_weapon_by_index(self, index: int):
        if index < 0 or index >= len(self.all_weapon):
            return
        self._set_weapon(self.all_weapon[index])

    def _change_in_cooldown(self):
        MAX_CONSECUTIVE_CHANGE = 2
        COOLDOWN = 2000  # ms
        self.weapon_change_energy += self.current_time - self.last_reload_time
        self.last_reload_time = self.current_time
        self.weapon_change_energy = utils.normalize(self.weapon_change_energy, 0, MAX_CONSECUTIVE_CHANGE * COOLDOWN)
        if self.weapon_change_energy < COOLDOWN:
            return True
        self.weapon_change_energy -= COOLDOWN
        return False

    def change_weapon(self, weapon=None):
        if weapon is None:
            self.cycle_weapon()
        elif isinstance(weapon, WeaponType):
            self._set_weapon(weapon)
        elif isinstance(weapon, int):
            self.set_weapon_by_index(weapon)
        else:
            raise TypeError("Invalid weapon type")

    def _get_bullet_count(self) -> int:
        if self.weapon.growth_factor != 0:
            bullet_count = self.weapon.min_bullet_count + int((self.weapon.level - 1) * self.weapon.growth_factor)
            return utils.normalize(bullet_count, self.weapon.min_bullet_count, self.weapon.bullet_count)
        else:
            return self.weapon.bullet_count

    def _fire_lazer(self):
        lazer_dy = self.dy / self.hypot * constants.BULLET_RADIUS
        lazer_dx = self.dx / self.hypot * constants.BULLET_RADIUS
        for i in range(self.bullet_count):
            self.game.bullets.append(Bullet(
                self.player.x + lazer_dx * i,
                self.player.y + lazer_dy * i,
                self.angle,
                weapon=self.weapon
            ))

    # def _fire_shotgun(self):
    #     direction_count = self.bullet_count
    #     angle_offset = math.pi * 0.4 / direction_count
    #     for i in range(self.bullet_count):
    #         offset = (i % direction_count - (direction_count - 1) / 2) * angle_offset
    #         shoot_angle = self.angle + offset
    #         speed = random.uniform(self.weapon.speed / 2, self.weapon.speed)
    #         self.bullets_list.append(
    #             Bullet(
    #                 self.player.x,
    #                 self.player.y,
    #                 shoot_angle,
    #                 speed=speed,
    #                 weapon=self.weapon
    #             ))

    def _fire_missile(self):
        direction_count = self.bullet_count
        angle_offset = math.pi * 2 / direction_count
        target = Missile.find_target_at(self.mx, self.my, self.game.enemies)
        for i in range(self.bullet_count):
            offset = (i % direction_count - (direction_count - 1) / 2) * angle_offset
            shoot_angle = self.angle + offset
            self.bullets_list.append(Missile(self.player.x, self.player.y, shoot_angle, self.game.enemies, target,
                                     dmg=self.weapon.dmg))

    def _fire_default(self):
        if self.weapon.bullet_class is MISSILE_CLASS:
            return self._fire_missile()
        elif self.weapon.bullet_class is LAZER_CLASS:
            return self._fire_lazer()
        elif self.weapon.bullet_class is NOVA_CLASS:
            return self._fire_nova()
        if self.bullet_count == 0:
            return
        angle_offset = self.weapon.spread / self.bullet_count
        for i in range(self.bullet_count):
            offset = (i - (self.bullet_count - 1) / 2) * angle_offset
            shoot_angle = self.angle + offset
            bullet_angle = self.angle + offset * self.weapon.offset_factor
            dy, dx = math.sin(shoot_angle) * self.weapon.spawn_radius, math.cos(shoot_angle) * self.weapon.spawn_radius
            dy, dx = dy - math.sin(self.angle) * self.weapon.spawn_radius, dx - math.cos(self.angle) * self.weapon.spawn_radius
            self.bullets_list.append(Bullet(
                self.player.x + dx,
                self.player.y + dy,
                bullet_angle,
                weapon=self.weapon
            ))

    def _fire_nova(self):
        mx, my = self.game.get_mouse_pos()
        print(self.bullet_count)
        for i in range(self.bullet_count):
            self.game.water_particle_handler.spawn_at(mx, my)
        self.game.water_particle_handler.attract_to(mx, my)

    def _update_fire_constants(self):
        self.mx, self.my = self.game.get_mouse_pos()
        self.dy, self.dx = self.my - self.player.y, self.mx - self.player.x
        self.hypot = math.hypot(self.dy, self.dx)
        self.angle = math.atan2(self.dy, self.dx)
        self.bullet_count = self._get_bullet_count()

    @property
    def overdrive_on(self) -> bool:
        return self.current_time - self._overdrive_start_time < constants.OVERDRIVE_DURATION

    def _update_overdrive(self):
        if self.overdrive_on:
            return
        self.overdrive_end()

    def fire(self):
        if self.weapon is None:
            return
        if self.current_time - self.last_shot_time.get(self.weapon, -10000000000) < self.weapon.shot_delay:
            return
        self.last_shot_time[self.weapon] = self.current_time

        self._update_overdrive()
        self._update_fire_constants()
        
        fire_dict = {
            LAZER_CLASS: self._fire_lazer,
            MISSILE_CLASS: self._fire_missile,
            NOVA_CLASS: self._fire_nova
        }
        # fire according to matched weapon and function
        fire_func = fire_dict.get(self.weapon.bullet_class, self._fire_default)
        fire_func()
        # self._fire_default()

        self.player.recoil(self.angle, self.weapon.recoil)

    def on_mouse_up(self):
        if self.weapon.bullet_class is NOVA_CLASS:
            self.game.water_particle_handler.release(
                *self.game.get_mouse_pos(),
                self.game.get_mouse_angle(),
                self.weapon.speed,
                self.player
            )
