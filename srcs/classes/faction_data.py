from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.game_data import GameData


class FactionData:
    def __init__(self, game_data: GameData, target_list: list[GameParticle], parent_list: list[GameParticle],):
        self.game_data: GameData = game_data
        self.target_list: list[GameParticle] = target_list
        self.parent_list: list[GameParticle] = parent_list