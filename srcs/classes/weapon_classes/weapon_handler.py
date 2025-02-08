import copy
from typing import Optional


from srcs import constants, utils
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.weapon_classes.general_weapon import BaseWeapon


class WeaponHandler:
    def __init__(self, unit: BaseUnit, weapons: Optional[list[BaseWeapon]] = None):
        self.unit: BaseUnit = unit
        self.weapon: Optional[BaseWeapon] = None
        self.all_weapons: list[BaseWeapon] = []
        self.reinit_weapons(weapons)
        self.change_cd = 2000  # ms
        self.is_first_shot = True
        self.weapon_change_energy = 10000
        self.last_charge_time = 0

    def reinit_weapons(self, weapons: list[BaseWeapon] | BaseWeapon | None = None):
        if isinstance(weapons, list):
            weapons = [weapon.copy() for weapon in weapons if isinstance(weapon, BaseWeapon)]
        elif isinstance(weapons, BaseWeapon):
            weapons = [weapons.copy()]
        else:
            weapons = []

        for w in weapons:
            w.mix_bullet_color_with(self.unit.get_greatest_parent().color)
        self.weapon: Optional[BaseWeapon] = weapons[0] if weapons else None
        self.all_weapons = weapons

    def is_max(self):
        return self.weapon.level.is_max()

    @property
    def current_time(self):
        return self.unit.faction.game_data.current_time

    @property
    def level_str(self):
        if self.weapon is None:
            return
        return self.weapon.level.__str__()

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
    def overdrive_percentage(self):
        return self.weapon.get_overdrive_reload_percentage(self.current_time)

    @overdrive_percentage.setter
    def overdrive_percentage(self, val):
        self.weapon.set_overdrive_reload_percentage(self.current_time, val)

    @property
    def overdrive_cd(self):
        return self.weapon.get_overdrive_cd(self.current_time)

    @overdrive_cd.setter
    def overdrive_cd(self, val):
        if val < 0.0:
            val = 0.0
        self.weapon.set_overdrive_cd(self.current_time, self.overdrive_cd + val)

    def overdrive_start(self):
        if not self.weapon:
            return
        self.weapon.start_overdrive_try(self.current_time)

    def upgrade_weapon(self, amount=1):
        if self.weapon.level.is_max():
            self.overdrive_cd -= constants.OVERDRIVE_CD * 0.25
        else:
            self.weapon.level.level_up(amount)

    def change_weapon(self, weapon=None):
        if weapon is None:
            self.cycle_weapon()
        elif isinstance(weapon, BaseWeapon):
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

    def _set_weapon(self, weapon: BaseWeapon):
        if self.weapon == weapon:
            return
        if self._change_in_cooldown():
            return
        if weapon.name in [w.name for w in self.all_weapons]:
            weapon = next(w for w in self.all_weapons if w.name == weapon.name)
        else:
            weapon = weapon.copy()
            self.all_weapons.append(weapon)
        self.weapon = weapon
        self.is_first_shot = True

    def _change_in_cooldown(self):
        max_consecutive_change = 1
        self.weapon_change_energy += self.current_time - self.last_charge_time
        self.last_charge_time = self.current_time
        self.weapon_change_energy = utils.clamp(self.weapon_change_energy, 0,
                                                max_consecutive_change * self.change_cd)
        return self.weapon_change_energy < self.change_cd

    def fire(self, target_x: float, target_y: float, **kwargs):
        if not self.weapon:
            return
        self.weapon.fire(self.unit, target_x, target_y, **kwargs)

    def __str__(self):
        return f"{self.name:15} {self.level_str}"