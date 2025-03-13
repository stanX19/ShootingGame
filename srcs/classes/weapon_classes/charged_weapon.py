import math
from collections.abc import Callable

from srcs.classes.effect import Effect
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.game_data import GameData
from srcs.classes.weapon_classes.general_weapon import GeneralWeapon
from srcs.classes.weapon_classes.reload_counter import CooldownTimer
from srcs.constants import PLAYER_RADIUS, OVERDRIVE_DURATION, OVERDRIVE_CD, EXPLOSION_COLOR


class ChargeParticle(Effect):
    def __init__(self, unit: BaseUnit, death_callback: Callable, game_data: GameData, x: int, y: int,
                 radius: float = 50, charge_lifespan: int = 10, color=EXPLOSION_COLOR):
        super().__init__(game_data, x, y, 0, 0,
                         lifespan=charge_lifespan,
                         rad=radius,
                         target_rad=0,
                         color=color,
                         fade_off=False,
                         fade_in=True)
        self.holder = unit
        self.death_callback = death_callback
    
    def on_death(self, *args, **kwargs) -> None:
        self.death_callback()

    def move(self):
        self.holder.speed = 0
        super().move()

# TODO:
#  make charged weapon a wrapper instead of a weapon itself
class ChargedWeapon(GeneralWeapon):
    def __init__(
            self,
            name: str,
            reload: int = 200,
            recoil: float = 0,
            offset_factor: float = 1.0,
            spread: float = math.pi * 2,
            spawn_radius: float = 0,
            bullet_class: type[FactionParticle] = Bullet,
            min_count: int = 1,
            max_count: int = 1,
            growth_factor: int = 1,
            overdrive_duration: float = OVERDRIVE_DURATION,
            overdrive_cooldown: float = OVERDRIVE_CD,
            charge_lifespan: int = 3,
            **bullet_kwargs,
    ):
        super().__init__(name, reload, recoil, offset_factor, spread, spawn_radius, bullet_class,
                         min_count, max_count, growth_factor,
                         overdrive_duration, overdrive_cooldown, **bullet_kwargs)
        self._charge_lifespan = charge_lifespan

    def _shoot(self, unit: BaseUnit, target_x: float, target_y: float) -> list[GameParticle]:
        shoot_angle = unit.angle_with_cord(target_x, target_y)
        self._spawner.spawn_radius = unit.rad
        new_bullets = self._spawner.circular_spawn(
            unit.x, unit.y, shoot_angle, self.level.bullet_count, unit
        )
        chargers = []
        for bullet in new_bullets:
            charger = ChargeParticle(unit,
                                     lambda : unit.faction.parent_list.append(bullet),
                                     unit.faction.game_data,
                                     bullet.x,
                                     bullet.y,
                                     radius=unit.rad * 2,
                                     color=bullet.color,
                                     charge_lifespan=self._charge_lifespan)
            chargers.append(charger)
        unit.faction.game_data.effects.extend(chargers)
        return chargers