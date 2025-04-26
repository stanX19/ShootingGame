import math

from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.faction_particle import FactionParticle
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.entity.missile import Missile
from srcs.classes.weapon_classes.general_weapon import GeneralWeapon
from srcs.constants import PLAYER_RADIUS, UNIT_RADIUS


class MissileWeapon(GeneralWeapon):
    def __init__(
            self,
            name: str,
            reload: int = 200,
            recoil: float = 0,
            offset_factor: float = 1.0,
            spread: float = math.pi * 2,
            spawn_radius: float = UNIT_RADIUS,
            bullet_class: type[FactionParticle]=Missile,
            max_count: int = 1,
            growth_factor: float = 1,
            **missile_kwargs,
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
            **missile_kwargs,
        )

    def _shoot(self, unit: BaseUnit, target_x: float, target_y: float) -> list[GameParticle]:
        target = unit.target or Missile.find_target_at(target_x, target_y, unit.faction.target_list)

        spawned_missiles: list[GameParticle] = super()._shoot(unit, target_x, target_y)

        for missile in spawned_missiles:
            missile.target = target

        return spawned_missiles