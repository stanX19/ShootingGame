from __future__ import annotations
from srcs.classes.entity.bullet import Bullet
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.faction_data import FactionData
from srcs.constants import *
from srcs.classes.game_data import GameData
from srcs.classes.effect import Effect


class Explosive(Bullet):
    def __init__(self, faction: FactionData, x: float, y: float, angle: float,
                 radius=None,
                 speed=None,
                 hp=1, dmg=10, lifespan=None, weapon=None,
                 color=None, explosion_color=EXPLOSION_COLOR, projectile_dmg=1,
                 **kwargs):
        super().__init__(faction, x, y, angle, speed, radius, color, hp, dmg, lifespan, weapon, **kwargs)
        self.explosion_color = explosion_color
        self.explosion_dmg = dmg
        self.dmg = projectile_dmg

    def on_death(self):
        self.faction.parent_list.append(Effect(self.faction.game_data, self.x, self.y, self.angle, 0,
                                            rad=self.rad,
                                            hp=10000000,
                                            dmg=self.explosion_dmg,
                                            lifespan=10,
                                            color=self.explosion_color,
                                            fade_off=True,
                                            target_rad = self.rad * 10))
        # self.game_data.bullets.append(Bullet(self.game_data, self.x, self.y, self.angle, 0, self.rad * 10, (0, 0, 0),
        #                                      100000000, self.dmg / 10, lifespan=10))
        return super().on_death()
