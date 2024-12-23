from __future__ import annotations
from srcs.classes.bullet import Bullet
from srcs.classes.game_particle import GameParticle
from srcs.constants import *
from srcs.classes.game_data import GameData
from srcs.classes.effect import Effect


class Explosive(Bullet):
    def __init__(self, game_data: GameData, parent_list: list[GameParticle], x: float, y: float, angle: float,
                 radius=None,
                 speed=None,
                 hp=1, dmg=10, lifespan=None, weapon=None,
                 color=None, explosion_color=EXPLOSION_COLOR):
        super().__init__(game_data, parent_list, x, y, angle, speed, radius, color, hp, dmg, lifespan, weapon)
        self.explosion_color = explosion_color

    def on_death(self):
        self.parent_list.append(Effect(self.game_data, self.x, self.y, self.angle, 0,
                                            rad=self.rad,
                                            hp=10000000,
                                            dmg=self.dmg / 5,
                                            lifespan=10,
                                            color=self.explosion_color,
                                            fade_off=True,
                                            target_rad = self.rad * 10))
        # self.game_data.bullets.append(Bullet(self.game_data, self.x, self.y, self.angle, 0, self.rad * 10, (0, 0, 0),
        #                                      100000000, self.dmg / 10, lifespan=10))
        return super().on_death()
