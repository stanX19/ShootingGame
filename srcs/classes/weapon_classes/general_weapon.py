import math
from typing import override

from srcs import utils
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.base_weapon import BaseWeapon
from srcs.classes.weapon_classes.bullet_spawner import BulletSpawner
from srcs.constants import PLAYER_RADIUS, OVERDRIVE_DURATION, OVERDRIVE_CD


class GeneralWeapon(BaseWeapon):
    def __init__(
            self,
            name: str,
            reload: int = 200,
            recoil: float = 0,
            offset_factor: float = 1.0,
            spread: float = math.pi * 2,
            spawn_radius: float = 0,
            bullet_class: type[Bullet] = Bullet,
            max_level: int = 1,
            min_count: int = 1,
            max_count: int = 1,
            growth_factor: int = 1,
            overdrive_duration: float = OVERDRIVE_DURATION,
            overdrive_cooldown: float = OVERDRIVE_CD,
            angle_offset: float = 0.0,
            **bullet_kwargs,
    ):
        super().__init__(name, max_level, min_count, max_count, growth_factor,
                         reload, overdrive_duration, overdrive_cooldown, **bullet_kwargs)
        self._spawner = BulletSpawner(self._bullet_kwargs, bullet_class=bullet_class, spread=spread,
                                      offset_factor=offset_factor, spawn_radius=spawn_radius,
                                      angle_offset=angle_offset)
        sample = self._spawner.get_sample()
        self._bullet_color = sample.color
        self._bullet_speed = sample.speed
        self._recoil = recoil

    @override
    def get_speed(self, unit: BaseUnit) -> float:
        return max(unit.speed - self._recoil, self._bullet_speed)

    @override
    def mix_bullet_color_with(self, color):
        self.update_bullet(
            color=utils.color_mix(color, self._bullet_color, 1.0, 0.5)
        )

    @override
    def update_bullet(self, **kwargs):
        self._bullet_kwargs.update_kwargs(**kwargs)

    @override
    def change_bullet_class(self, new_bullet_class: type[GameParticle]):
        self._spawner.bullet_class = new_bullet_class

    @override
    def _start_overdrive(self):
        self._shoot_cd.shoot_cd *= 0.1  # Drastically reduce shooting cooldown during overdrive

    @override
    def _end_overdrive(self):
        self._shoot_cd.shoot_cd /= 0.1

    @override
    def _shoot(self, unit: BaseUnit, target_x: float, target_y: float) -> list[GameParticle]:
        shoot_angle = unit.angle_with_cord(target_x, target_y)
        new_bullets = self._spawner.circular_spawn(
            unit.x, unit.y, shoot_angle, self.level.bullet_count, unit
        )

        unit.faction.parent_list.extend(new_bullets)
        self._apply_recoil(unit, shoot_angle, self._recoil)
        return new_bullets

    def _apply_recoil(self, unit: BaseUnit, shoot_angle: float, magnitude: float) -> None:
        """Applies recoil to the unit."""
        unit.xv -= math.cos(shoot_angle) * magnitude
        unit.yv -= math.sin(shoot_angle) * magnitude
