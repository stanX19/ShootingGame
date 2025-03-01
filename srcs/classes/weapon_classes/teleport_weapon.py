import math

from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.entity.lazer import Lazer
from srcs.classes.weapon_classes.general_weapon import GeneralWeapon
from srcs.constants import UNIT_RADIUS, BULLET_RADIUS


class TeleportWeapon(GeneralWeapon):
    def __init__(
            self,
            name: str,
            reload: int = 200,
            recoil: float = 0,
            offset_factor: float = 1.0,
            spread: float = math.pi * 2,
            spawn_radius: float = UNIT_RADIUS,
            bullet_class: type[Lazer]=Lazer,
            max_count: int = 1,
            growth_factor: float = 1,
            **lazer_kwargs,
    ):
        """
        Initializes the MissileWeapon with specific settings for missiles.
        """
        super().__init__(
            name=name,
            reload=reload,
            recoil=recoil,
            offset_factor=offset_factor,
            spread=spread,
            spawn_radius=spawn_radius,
            bullet_class=bullet_class,
            max_count=max_count,
            growth_factor=growth_factor,
            **lazer_kwargs,
        )

    def _shoot(self, unit: BaseUnit, target_x: float, target_y: float) -> list[GameParticle]:
        shoot_angle = unit.angle_with_cord(target_x, target_y)
        bullet_count = self.level.bullet_count
        recoil = self._recoil * bullet_count

        new_bullets: list[Lazer] = self._spawner.circular_spawn(
            unit.x, unit.y, shoot_angle, 1, unit
        )

        unit.faction.parent_list.extend(new_bullets)
        try:
            self._apply_recoil(unit, new_bullets[0].angle, recoil)
            new_bullets[0].length = abs(recoil)
        except IndexError:
            pass
        return new_bullets
