import copy
import math
from typing import Optional

from srcs import constants, utils
from srcs.classes.base_unit import BaseUnit
from srcs.classes.bullet import Bullet
from srcs.classes.explosive import Explosive
from srcs.classes.game_data import GameData
from srcs.classes.lazer import Lazer
from srcs.classes.missile import Missile
from srcs.classes.weapons import WeaponType, LAZER_CLASS, MISSILE_CLASS, NOVA_CLASS, EXPLOSIVE_CLASS


class WeaponHandler:
    def __init__(self, game_data: GameData, unit: BaseUnit, weapons: Optional[list[WeaponType]] = None):
        self.game_data: GameData = game_data
        self.unit: BaseUnit = unit
        self.weapon: Optional[WeaponType] = None
        self.all_weapons: list[WeaponType] = []
        self.reinit_weapons(weapons)
        self.change_cd = 2000  # ms
        self.is_first_shot = True
        self.last_shot_time = {}
        self.weapon_change_energy = 10000
        self.last_reload_time = 0
        self.bullet_count: int = 1
        self._overdrive_end_time = -constants.OVERDRIVE_CD
        self._overdrive_start_time = -constants.OVERDRIVE_CD
        self.overdrive_weapon: Optional[WeaponType] = None
        self.angle: float = 0.0
        self.target_x: float = 0.0
        self.target_y: float = 0.0

    def reinit_weapons(self, weapons: Optional[list[WeaponType]] = None):
        if isinstance(weapons, list):
            weapons = [copy.copy(weapon) for weapon in weapons if isinstance(weapon, WeaponType)]
        elif isinstance(weapons, WeaponType):
            weapons = [copy.copy(weapons)]
        else:
            weapons = []

        for w in weapons:
            w.color = utils.color_mix(self.unit.color, w.color)
        self.weapon: Optional[WeaponType] = weapons[0] if weapons else None
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
        return self.weapon.name if self.weapon else "None"

    @property
    def overdrive_cd(self):
        return max(0.0, constants.OVERDRIVE_CD - (self.unit.game_data.current_time - self._overdrive_end_time))

    @overdrive_cd.setter
    def overdrive_cd(self, val):
        if val < 0.0:
            val = 0.0
        self._overdrive_end_time = self.unit.game_data.current_time - constants.OVERDRIVE_CD + val

    def overdrive_start(self):
        if self.overdrive_weapon:
            return
        if self.overdrive_cd:
            return
        self._overdrive_start_time = self.unit.game_data.current_time
        self._overdrive_end_time = self.unit.game_data.current_time
        self.overdrive_weapon = self.weapon
        self.last_shot_time[self.overdrive_weapon] = -self.weapon.shot_delay
        self.overdrive_weapon.rad *= 2
        self.overdrive_weapon.dmg *= 5
        self.overdrive_weapon.hp *= 2
        self.overdrive_weapon.shot_delay /= 10
        self.overdrive_weapon.recoil *= 2

    def overdrive_end(self):
        if not self.overdrive_weapon:
            return
        self.overdrive_weapon.rad /= 2
        self.overdrive_weapon.dmg /= 5
        self.overdrive_weapon.hp /= 2
        self.overdrive_weapon.shot_delay *= 10
        self.overdrive_weapon.recoil /= 2
        self.overdrive_weapon = None

    def upgrade_weapon(self):
        if self.weapon.is_max_lvl():
            self.overdrive_cd -= constants.OVERDRIVE_CD * 0.25
        else:
            self.weapon.level += 1

    def change_weapon(self, weapon=None):
        if weapon is None:
            self.cycle_weapon()
        elif isinstance(weapon, WeaponType):
            self._set_weapon(weapon)
        elif isinstance(weapon, int):
            self.set_weapon_by_index(weapon)
        else:
            raise TypeError("Invalid weapon type")

    def cycle_weapon(self, change: int = 1):
        idx = (self.index + change) % len(self.all_weapons)
        self._set_weapon(self.all_weapons[idx])

    def set_weapon_by_index(self, index: int):
        if 0 <= index < len(self.all_weapons):
            self._set_weapon(self.all_weapons[index])

    def _set_weapon(self, weapon: WeaponType):
        if self.weapon.name == weapon.name:
            return
        if self._change_in_cooldown():
            return
        if weapon.name in [w.name for w in self.all_weapons]:
            weapon = next(w for w in self.all_weapons if w.name == weapon.name)
        else:
            weapon = copy.copy(weapon)
            self.all_weapons.append(weapon)
        self.overdrive_end()
        self.weapon = weapon
        self.is_first_shot = True

    def _change_in_cooldown(self):
        max_consecutive_change = 1
        self.weapon_change_energy += self.unit.game_data.current_time - self.last_reload_time
        self.last_reload_time = self.unit.game_data.current_time
        self.weapon_change_energy = utils.normalize(self.weapon_change_energy, 0, max_consecutive_change * self.change_cd)
        return self.weapon_change_energy < self.change_cd

    def _get_bullet_count(self) -> int:
        if self.weapon.growth_factor != 0:
            bullet_count = self.weapon.min_bullet_count + int((self.weapon.level - 1) * self.weapon.growth_factor)
            return utils.normalize(bullet_count, self.weapon.min_bullet_count, self.weapon.bullet_count)
        else:
            return self.weapon.bullet_count

    def _apply_recoil(self, shoot_angle, magnitude):
        self.unit.xv -= math.cos(shoot_angle) * magnitude
        self.unit.yv -= math.sin(shoot_angle) * magnitude

    def fire(self, target_x: float, target_y: float):
        if not self.weapon:
            return
        if self.unit.game_data.current_time - self.last_shot_time.get(self.weapon, -10000000000) < self.weapon.shot_delay:
            return

        self.last_shot_time[self.weapon] = self.unit.game_data.current_time
        self.angle = self.unit.angle_with_cord(target_x, target_y)
        self.target_x = target_x
        self.target_y = target_y
        self.bullet_count = self._get_bullet_count()

        # Fire bullets based on the weapon type
        fire_dict = {
            LAZER_CLASS: self._fire_lazer,
            MISSILE_CLASS: self._fire_missile,
            NOVA_CLASS: self._fire_nova,
            # UNIT_CLASS: self._fire_unit,
        }
        fire_func = fire_dict.get(self.weapon.bullet_class, self._fire_default)
        fire_func()
        self._apply_recoil(self.angle, self.weapon.recoil)

    def _fire_lazer(self):
        # lazer_dy = math.sin(self.angle) * self.weapon.rad
        # lazer_dx = math.cos(self.angle) * self.weapon.rad
        # for i in range(self.bullet_count):
        #     self.unit.parent_list.append(Bullet(
        #         self.game_data,
        #         self.unit.x + lazer_dx * i,
        #         self.unit.y + lazer_dy * i,
        #         self.angle,
        #         weapon=self.weapon
        #     ))
        self.unit.parent_list.append(Lazer(self.game_data, self.unit.parent_list, self.unit.x, self.unit.y, self.angle, weapon=self.weapon))

    def _fire_missile(self):
        direction_count = self.bullet_count
        angle_offset = math.pi * 2 / direction_count
        target = Missile.find_target_at(self.target_x, self.target_y, self.unit.target_list)
        for i in range(self.bullet_count):
            offset = (i % direction_count - (direction_count - 1) / 2) * angle_offset
            shoot_angle = self.angle + offset
            self.unit.parent_list.append(Missile(self.game_data, self.unit.parent_list,
                                                 self.unit.x, self.unit.y,
                                                 shoot_angle, self.unit.target_list, target,
                                                 speed=self.weapon.speed,
                                                 dmg=self.weapon.dmg,
                                                 hp=self.weapon.hp,
                                                 lifespan=self.weapon.lifespan
                                                 ))

    def _fire_default(self):
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
            self.unit.parent_list.append(bullet_class(
                self.game_data,
                self.unit.parent_list,
                self.unit.x + dx,
                self.unit.y + dy,
                bullet_angle,
                weapon=self.weapon
            ))

    def _fire_nova(self):
        mx, my = self.game_data.get_mouse_pos()
        for i in range(self.bullet_count):
            self.game_data.water_particle_handler.spawn_at(mx, my)
        self.game_data.water_particle_handler.attract_to(mx, my)



