from __future__ import annotations

from srcs.classes.effect import Effect
from srcs.classes.entity.bullet import Bullet
from srcs.classes.faction_data import FactionData
from srcs.constants import *


class Explosive(Bullet):
    def __init__(self, faction: FactionData, x: float = 0.0, y: float = 0.0, angle: float = 0.0,
                 speed=BULLET_SPEED, radius=BULLET_RADIUS,
                 color=BULLET_COLOR, hp=1.0, dmg=1.0, lifespan=float('inf'),
                 explosion_color=EXPLOSION_COLOR, projectile_dmg=1,
                 explosion_rad: float=None, explosion_lifespan: int=10,
                 **kwargs):
        super().__init__(faction, x, y, angle, speed, radius, color, hp, dmg, lifespan, **kwargs)
        self.explosion_color = explosion_color
        self.explosion_dmg = dmg
        self.dmg = projectile_dmg
        self.explosion_rad = explosion_rad if explosion_rad is not None else self.rad * 5
        self.explosion_lifespan = explosion_lifespan

    def on_death(self):
        self.faction.parent_list.append(Effect(self.faction.game_data, self.x, self.y, self.angle, 0,
                                               rad=self.rad,
                                               hp=10000000,
                                               dmg=self.explosion_dmg,
                                               lifespan=self.explosion_lifespan,
                                               color=self.explosion_color,
                                               fade_off=True,
                                               target_rad=self.explosion_rad,
                                               parent=self))
        # self.game_data.bullets.append(Bullet(self.game_data, self.x, self.y, self.angle, 0, self.rad * 10, (0, 0, 0),
        #                                      100000000, self.dmg / 10, lifespan=10))
        return super().on_death()
