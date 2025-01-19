import math

from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.entity.missile import Missile
from srcs.classes.weapon_classes.general_weapon import GeneralWeapon
from srcs.constants import PLAYER_RADIUS


class MissileWeapon(GeneralWeapon):
    def __init__(
            self,
            name: str,
            reload: int = 200,
            recoil: float = 0,
            offset_factor: float = 0.1,
            spread: float = math.pi,
            spawn_radius: float = PLAYER_RADIUS * 5,
            max_level: int = 1,
            max_count: int = 1,
            growth_factor: int = 1,
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
            bullet_class=Missile,
            max_level=max_level,
            max_count=max_count,
            growth_factor=growth_factor,
            **missile_kwargs,
        )

    def fire(self, unit: BaseUnit, target_x: float, target_y: float) -> list[GameParticle]:
        target = Missile.find_target_at(target_x, target_y, unit.faction.target_list)

        spawned_missiles = super().fire(unit, target_x, target_y)

        for missile in spawned_missiles:
            missile.target = target

        return spawned_missiles
