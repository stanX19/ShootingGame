from __future__ import annotations
import math
import random
import copy
from typing import Optional

from srcs import constants
from srcs import utils
from srcs.classes.bullet import Bullet
from srcs.classes.explosive import Explosive
from srcs.classes.missile import Missile
from srcs.classes.enemy import ShootingEnemy
from srcs.classes.weapons import WeaponType
from srcs.classes.weapons import MISSILE_CLASS, LAZER_CLASS, NOVA_CLASS, EXPLOSIVE_CLASS, UNIT_CLASS
from srcs.classes.game_data import GameData


class WeaponHandler:
    def __init__(self, game_data: GameData, weapons: [None, list[WeaponType], type] = None):
        self.weapon: Optional[WeaponType] = None
        self.all_weapons: list[WeaponType] = []
        self.reinit_weapons(weapons)
        self.change_cd = 2000  # ms
        self.is_first_shot = True
        self.last_shot_time = {}
        self.weapon_change_energy = 10000
        self.last_reload_time = 0
        self.game_data: GameData = game_data
        self.mx, self.my = 0, 0
        self.dy, self.dx = 0, 0
        self.hypot = 0.0
        self.angle = 0.0
        self.bullet_count = 1
        self._overdrive_end_time = -constants.OVERDRIVE_CD
        self._overdrive_start_time = -constants.OVERDRIVE_CD
        self.overdrive_weapon = None

    def reinit_weapons(self, weapons: [None, list[WeaponType], type] = None):
        if isinstance(weapons, list):
            weapons = [copy.copy(weapon) for weapon in weapons if isinstance(weapon, WeaponType)]
        elif isinstance(weapons, WeaponType):
            weapons = [weapons]
        elif isinstance(weapons, type):
            weapons = [copy.copy(attr) for attr in vars(weapons).values() if isinstance(attr, WeaponType)]
        else:
            weapons = []

        self.weapon: [WeaponType, None] = weapons[0] if weapons else None
        self.all_weapons = weapons

    @property
    def level_str(self):
        return self.weapon.level if not self.weapon.is_max_lvl() else "Max"

    @property
    def index(self):
        try:
            return self.all_weapons.index(self.weapon)
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
        return max(0.0, constants.OVERDRIVE_CD - (self.game_data.current_time - self._overdrive_end_time))

    @overdrive_cd.setter
    def overdrive_cd(self, val):
        if val < 0.0:
            val = 0.0
        self._overdrive_end_time = self.game_data.current_time - constants.OVERDRIVE_CD + val

    def overdrive_start(self):
        if self.overdrive_weapon:
            return
        if self.overdrive_cd:
            return
        self._overdrive_start_time = self.game_data.current_time
        self._overdrive_end_time = self.game_data.current_time
        self.overdrive_weapon = self.weapon
        self.last_shot_time[self.overdrive_weapon] = -self.weapon.shot_delay
        self.overdrive_weapon.rad *= 2
        self.overdrive_weapon.dmg *= 5
        self.overdrive_weapon.hp *= 2
        self.overdrive_weapon.shot_delay /= 10
        self.overdrive_weapon.recoil *= 2
        constants.MAX_PARTICLE_COUNT *= 2
        # self.overdrive_weapon.speed *= 2

    def overdrive_end(self):
        if not self.overdrive_weapon:
            return
        self.overdrive_weapon.rad /= 2
        self.overdrive_weapon.dmg /= 5
        self.overdrive_weapon.hp /= 2
        self.overdrive_weapon.shot_delay *= 10
        self.overdrive_weapon.recoil /= 2
        constants.MAX_PARTICLE_COUNT /= 2
        # self.overdrive_weapon.speed /= 2
        self.overdrive_weapon = None

    def upgrade_weapon(self):
        if self.weapon.is_max_lvl():
            self.overdrive_cd -= constants.OVERDRIVE_CD * 0.25
        else:
            self.weapon.level += 1

    def _set_weapon(self, weapon: WeaponType):
        if self.weapon.name == weapon.name:
            return
        if self._change_in_cooldown():
            return
        if weapon.name in [w.name for w in self.all_weapons]:
            weapon = [w for w in self.all_weapons if w.name == weapon.name][0]
        else:
            weapon = copy.copy(weapon)
            self.all_weapons.append(weapon)
        self.on_mouse_up()
        self.overdrive_end()
        self.weapon = weapon
        self.is_first_shot = True

    def cycle_weapon(self, change: int = 1):
        idx = (self.index + change) % len(self.all_weapons)
        self._set_weapon(self.all_weapons[idx])

    def set_weapon_by_index(self, index: int):
        if index < 0 or index >= len(self.all_weapons):
            return
        self._set_weapon(self.all_weapons[index])

    def _change_in_cooldown(self):
        MAX_CONSECUTIVE_CHANGE = 1
        self.weapon_change_energy += self.game_data.current_time - self.last_reload_time
        self.last_reload_time = self.game_data.current_time
        self.weapon_change_energy = utils.normalize(self.weapon_change_energy, 0, MAX_CONSECUTIVE_CHANGE * self.change_cd)
        if self.weapon_change_energy < self.change_cd:
            return True

        # self.weapon_change_energy -= change_cd
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
            self.game_data.bullets.append(Bullet(
                self.game_data,
                self.game_data.player.x + lazer_dx * i,
                self.game_data.player.y + lazer_dy * i,
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
    #                 self.data.player.x,
    #                 self.data.player.y,
    #                 shoot_angle,
    #                 speed=speed,
    #                 weapon=self.weapon
    #             ))

    def _fire_missile(self):
        direction_count = self.bullet_count
        angle_offset = math.pi * 2 / direction_count
        target = Missile.find_target_at(self.mx, self.my, self.game_data.enemies)
        for i in range(self.bullet_count):
            offset = (i % direction_count - (direction_count - 1) / 2) * angle_offset
            shoot_angle = self.angle + offset
            self.game_data.bullets.append(Missile(self.game_data, self.game_data.player.x, self.game_data.player.y,
                                                  shoot_angle, self.game_data.enemies, target, dmg=self.weapon.dmg))

    def _fire_unit(self):
        angle_offset = self.weapon.spread / self.bullet_count
        for i in range(self.bullet_count):
            offset = (i - (self.bullet_count - 1) / 2) * angle_offset
            shoot_angle = self.angle + offset
            bullet_angle = self.angle + offset * self.weapon.offset_factor
            dy, dx = math.sin(shoot_angle) * self.weapon.spawn_radius, math.cos(shoot_angle) * self.weapon.spawn_radius
            dy, dx = dy - math.sin(self.angle) * self.weapon.spawn_radius, dx - math.cos(
                self.angle) * self.weapon.spawn_radius
            self.game_data.bullets.append(ShootingEnemy(
                self.game_data,
                self.game_data.player.x + dx,
                self.game_data.player.y + dy,
                self.game_data.enemies,
                self.game_data.bullets,
                hp=self.weapon.hp,
                dmg=self.weapon.dmg,
                speed=self.weapon.speed,
                radius=self.weapon.rad,
                color=self.weapon.color,
            ))
    def _fire_default(self):
        if self.weapon.bullet_class is MISSILE_CLASS:
            return self._fire_missile()
        elif self.weapon.bullet_class is LAZER_CLASS:
            return self._fire_lazer()
        elif self.weapon.bullet_class is NOVA_CLASS:
            return self._fire_nova()
        if self.bullet_count == 0:
            return
        bullet_class = Bullet
        if self.weapon.bullet_class is EXPLOSIVE_CLASS:
            bullet_class = Explosive
        angle_offset = self.weapon.spread / self.bullet_count
        for i in range(self.bullet_count):
            offset = (i - (self.bullet_count - 1) / 2) * angle_offset
            shoot_angle = self.angle + offset
            bullet_angle = self.angle + offset * self.weapon.offset_factor
            dy, dx = math.sin(shoot_angle) * self.weapon.spawn_radius, math.cos(shoot_angle) * self.weapon.spawn_radius
            dy, dx = dy - math.sin(self.angle) * self.weapon.spawn_radius, dx - math.cos(self.angle) * self.weapon.spawn_radius
            self.game_data.bullets.append(bullet_class(
                self.game_data,
                self.game_data.player.x + dx,
                self.game_data.player.y + dy,
                bullet_angle,
                weapon=self.weapon
            ))

    def _fire_nova(self):
        mx, my = self.game_data.get_mouse_pos()
        for i in range(self.bullet_count):
            self.game_data.water_particle_handler.spawn_at(mx, my)
        self.game_data.water_particle_handler.attract_to(mx, my)

    def _update_fire_constants(self):
        self.mx, self.my = self.game_data.get_mouse_pos()
        self.dy, self.dx = self.my - self.game_data.player.y, self.mx - self.game_data.player.x
        self.hypot = math.hypot(self.dy, self.dx)
        self.angle = math.atan2(self.dy, self.dx)
        self.bullet_count = self._get_bullet_count()

    @property
    def overdrive_on(self) -> bool:
        return self.game_data.current_time - self._overdrive_start_time < constants.OVERDRIVE_DURATION

    def _update_overdrive(self):
        if self.overdrive_on:
            return
        self.overdrive_end()

    def fire(self):
        if self.weapon is None:
            return
        if self.game_data.current_time - self.last_shot_time.get(self.weapon, -10000000000) < self.weapon.shot_delay:
            return
        if self.is_first_shot:
            self.weapon_change_energy -= self.change_cd
            self.is_first_shot = False
        self.last_shot_time[self.weapon] = self.game_data.current_time

        self._update_overdrive()
        self._update_fire_constants()
        
        fire_dict = {
            LAZER_CLASS: self._fire_lazer,
            MISSILE_CLASS: self._fire_missile,
            NOVA_CLASS: self._fire_nova,
            UNIT_CLASS: self._fire_unit,
        }
        # fire according to matched weapon and function
        fire_func = fire_dict.get(self.weapon.bullet_class, self._fire_default)
        fire_func()
        # self._fire_default()

        self.game_data.player.recoil(self.angle, self.weapon.recoil)

    def on_mouse_up(self):
        if self.weapon.bullet_class is NOVA_CLASS:
            self.game_data.water_particle_handler.release(
                *self.game_data.get_mouse_pos(),
                self.game_data.get_mouse_angle(),
                self.weapon.speed,
                self.game_data.player
            )
