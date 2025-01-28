import copy
from typing import override

from pygame.gfxdraw import pixel

from srcs import utils
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.base_weapon import BaseWeapon
from srcs.classes.weapon_classes.reload_counter import CooldownTimer


class CompositeWeapon(BaseWeapon):
    def __init__(
            self,
            name: str,
            weapons: list[BaseWeapon],
            shoot_interval: int = 0,
    ):
        super().__init__(name)
        self._weapons = [copy.deepcopy(w) for w in weapons]
        self._interval_cd = CooldownTimer(shoot_interval)
        self._unlocked_index = 0

    @override
    def fire(self, unit: BaseUnit, target_x: float, target_y: float, **kwargs) -> list[GameParticle]:
        current_time = unit.faction.game_data.current_time

        if self._unlocked_index == len(self._weapons):
            if self._interval_cd.is_ended(current_time):
                self._unlocked_index = 1
            self._interval_cd.start_timer(current_time)

        if self._interval_cd.is_ended(current_time, auto_restart=True):
            self._unlocked_index += 1
        ret = sum([w.fire(unit, target_x, target_y, **kwargs) for w in self._weapons[:self._unlocked_index]], [])
        return ret

    @override
    def get_speed(self, unit: BaseUnit) -> float:
        return max(w.get_speed(unit) for w in self._weapons)

    @override
    def mix_bullet_color_with(self, color):
        for w in self._weapons:
            w.mix_bullet_color_with(color)

    def change_bullet_class(self, new_bullet_class: type[GameParticle]):
        for w in self._weapons:
            w.change_bullet_class(new_bullet_class)

    @override
    def start_overdrive_try(self, current_time: float):
        activated = any([w.start_overdrive_try(current_time) for w in self._weapons])
        if activated:
            self._unlocked_index = 1
        return activated

    @override
    def get_overdrive_cd(self, current_time: float):
        return min(w.get_overdrive_cd(current_time) for w in self._weapons)

    @override
    def set_overdrive_cd(self, current_time: float, new_cd: float):
        for w in self._weapons:
            w.set_overdrive_cd(current_time, new_cd)

    @override
    def get_overdrive_reload_percentage(self, current_time: float):
        return max(w.get_overdrive_reload_percentage(current_time) for w in self._weapons)

    @override
    def set_overdrive_reload_percentage(self, current_time: float, val: float):
        for w in self._weapons:
            w.set_overdrive_reload_percentage(current_time, val)

    @override
    def update_bullet(self, **kwargs):
        for w in self._weapons:
            w.update_bullet(**kwargs)

