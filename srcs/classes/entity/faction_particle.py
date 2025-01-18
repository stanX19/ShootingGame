from __future__ import annotations

from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.faction_data import FactionData


class FactionParticle(GameParticle):
    def __init__(self, faction_data: FactionData,
                 x: float, y: float, angle=0.0, speed=0.0, radius=1.0, color=(255, 255, 255), hp=1, dmg=1,
                 score=0, **kwargs):
        super().__init__(x, y, angle, speed, radius, color, hp, dmg, score, **kwargs)
        self.faction: FactionData = faction_data
