import math
from typing import override

from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.base_weapon import BaseWeapon
from srcs.classes.weapon_classes.bullet_spawner import BulletSpawner
from srcs.constants import PLAYER_RADIUS, OVERDRIVE_DURATION, OVERDRIVE_CD


class SpawnerWeapon(BaseWeapon):
    def __init__(
            self,
            name: str,
            reload: int = 200,
            offset_factor: float = 1.0,
            spread: float = math.pi * 2,
            spawn_radius: float = 0,
            bullet_class: type[Bullet] = Bullet,
            min_count: int = 1,
            max_count: int = 1,
            growth_factor: int = 1,
            overdrive_duration: float = OVERDRIVE_DURATION,
            overdrive_cooldown: float = OVERDRIVE_CD,
            angle_offset: float = 0.0,
            **bullet_kwargs,
    ):
        super().__init__(name, min_count, max_count, growth_factor,
                         reload, overdrive_duration, overdrive_cooldown, **bullet_kwargs)
        self._spawner = BulletSpawner(self._bullet_kwargs, bullet_class=bullet_class, spread=spread,
                                      offset_factor=offset_factor, spawn_radius=spawn_radius,
                                      angle_offset=angle_offset)

    @override
    def fire(self, unit: BaseUnit, target_x: float, target_y: float, **kwargs) -> list[GameParticle]:
        if not self._shoot_cd.is_ended(unit.faction.game_data.current_time, auto_restart=True):
            return []
        self.check_overdrive_end(unit.faction.game_data.current_time)
        shoot_angle = unit.angle_with_cord(target_x, target_y)
        self._spawner.spawn_radius = unit.rad - 10
        new_bullets: list[BaseUnit] = self._spawner.circular_spawn(
            unit.x, unit.y, shoot_angle, self.level.bullet_count, unit
        )
        for b in new_bullets:
            b.target = unit.target
        unit.faction.parent_list.extend(new_bullets)
        return new_bullets

    @override
    def update_bullet(self, **kwargs):
        self._bullet_kwargs.update_kwargs(**kwargs)

    @override
    def get_speed(self, unit: BaseUnit) -> float:
        return 0

    @override
    def mix_bullet_color_with(self, color):
        self.update_bullet(color=color)

    @override
    def change_bullet_class(self, new_bullet_class: type[GameParticle]):
        self._spawner.bullet_class = new_bullet_class

    @override
    def _start_overdrive(self):
        self._shoot_cd.shoot_cd *= 0.1

    @override
    def _end_overdrive(self):
        self._shoot_cd.shoot_cd /= 0.1

