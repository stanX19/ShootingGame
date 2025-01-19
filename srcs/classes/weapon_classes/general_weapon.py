import math

from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.faction_data import FactionData
from srcs.classes.weapon_classes.base_weapon import BaseWeapon
from srcs.classes.weapon_classes.bullet_spawner import BulletSpawner, BulletKwargsHandler
from srcs.classes.weapon_classes.level_handler import LevelHandler
from srcs.classes.weapon_classes.reload_counter import ReloadCounter
from srcs.constants import PLAYER_RADIUS


class GeneralWeapon(BaseWeapon):
    def __init__(
            self,
            name: str,
            reload: int = 200,
            recoil: float = 0,
            offset_factor: float = 1.0,
            spread: float = math.pi * 2,
            spawn_radius: float = PLAYER_RADIUS * 5,
            bullet_class: type[Bullet] = Bullet,
            max_level: int = 1,
            max_count: int = 1,
            growth_factor: int = 1,
            **bullet_kwargs,
    ):
        super().__init__(name, max_level)
        self.shoot_timer = ReloadCounter(reload)
        self.bullet_kwargs = BulletKwargsHandler(bullet_kwargs)
        self.spawner = BulletSpawner(self.bullet_kwargs, bullet_class=bullet_class, spread=spread,
                                     offset_factor=offset_factor, spawn_radius=spawn_radius)
        self.level = LevelHandler(max_level, max_count, growth_factor)
        self.recoil = recoil

    def fire(self, unit: BaseUnit, target_x: float, target_y: float) -> list[GameParticle]:
        if not self.shoot_timer.record_if_can_fire(unit.faction.game_data.current_time):
            return []

        shoot_angle = unit.angle_with_cord(target_x, target_y)
        new_bullets = self.spawner.circular_spawn(
            unit.x, unit.y, shoot_angle, self.level.bullet_count, unit
        )

        unit.faction.parent_list.extend(new_bullets)
        self._apply_recoil(unit, shoot_angle, self.recoil)
        return new_bullets

    def _apply_recoil(self, unit: BaseUnit, shoot_angle: float, magnitude: float) -> None:
        unit.xv -= math.cos(shoot_angle) * magnitude
        unit.yv -= math.sin(shoot_angle) * magnitude
