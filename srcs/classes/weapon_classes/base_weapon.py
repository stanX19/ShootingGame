import copy
from typing import final, Any

from srcs import utils
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.bullet_spawner import BulletKwargsHandler
from srcs.classes.weapon_classes.level_handler import LevelHandler
from srcs.classes.weapon_classes.reload_counter import CooldownTimer
from srcs.constants import BULLET_SPEED, BULLET_COLOR, OVERDRIVE_DURATION, OVERDRIVE_CD


class BaseWeapon:
    def __init__(self, name: str,
                 max_level: int = 1,
                 min_count: int = 1,
                 max_count: int = 1,
                 growth_factor: int = 1,
                 reload: int = 200,
                 overdrive_duration: float = OVERDRIVE_DURATION,
                 overdrive_cooldown: float = OVERDRIVE_CD,
                 **bullet_kwargs: dict[str: Any]):
        self.name: str = name
        self.level: LevelHandler = LevelHandler(max_level, min_count, max_count, growth_factor)

        # general handlers
        self._bullet_kwargs = BulletKwargsHandler(bullet_kwargs)
        self._shoot_cd = CooldownTimer(reload)
        self._overdrive_cd_timer = CooldownTimer(overdrive_cooldown)
        self._overdrive_active_timer = CooldownTimer(overdrive_duration)
        self._overdrive_is_active = False

    # ======================= MUST IMPLEMENT =======================

    def update_bullet(self, **kwargs):
        raise NotImplementedError(f"update_bullet() is not implemented in {type(self)}")

    def get_speed(self, unit: BaseUnit) -> float:
        raise NotImplementedError(f"get_speed() is not implemented in {type(self)}")

    def mix_bullet_color_with(self, color):
        raise NotImplementedError(f"mix_bullet_color_with() is not implemented in {type(self)}")

    def change_bullet_class(self, new_bullet_class: type[GameParticle]):
        raise NotImplementedError(f"change_bullet_class() is not implemented in {type(self)}")

    # ==========================OPTIONAL==========================

    def get_overdrive_cd(self, current_time: float):
        return self._overdrive_cd_timer.get_remaining_time(current_time)

    def set_overdrive_cd(self, current_time: float, new_cd: float):
        self._overdrive_cd_timer.set_remaining_time(current_time, new_cd)

    def get_overdrive_reload_percentage(self, current_time: float):
        return self._overdrive_cd_timer.get_reload_percentage(current_time)

    def set_overdrive_reload_percentage(self, current_time: float, val: float):
        return self._overdrive_cd_timer.set_reload_percentage(current_time, val)

    def start_overdrive_try(self, current_time: float) -> bool:
        if not self._overdrive_cd_timer.is_ended(current_time, auto_restart=True):
            return False
        if self._overdrive_is_active:
            self._end_overdrive()
        self._overdrive_active_timer.start_timer(current_time)
        self._start_overdrive()
        self._overdrive_is_active = True
        return True

    @final
    def check_overdrive_end(self, current_time: float):
        if not self._overdrive_is_active:
            return
        if not self._overdrive_active_timer.is_ended(current_time):
            return
        self._end_overdrive()
        self._overdrive_is_active = False


    def fire(self, unit: BaseUnit, target_x: float, target_y: float, **kwargs) -> list[FactionParticle]:
        """
        Fire with cd, calls _fire() if cd is zero
        :return: list of spawned particles
        """
        if not self._shoot_cd.is_ended(unit.faction.game_data.current_time, auto_restart=True):
            return []
        self.check_overdrive_end(unit.faction.game_data.current_time)
        return self._shoot(unit, target_x, target_y)

    def _shoot(self, unit: BaseUnit, target_x: float, target_y: float) -> list[FactionParticle]:
        raise NotImplementedError("_fire() must be implemented in derived classes.")

    def _start_overdrive(self):
        pass

    def _end_overdrive(self):
        pass

    def copy(self):
        return copy.deepcopy(self)

    def __repr__(self):
        return f"{type(self).__name__}<{self.name}>"