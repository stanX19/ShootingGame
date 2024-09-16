import math
from typing import Optional
from srcs.classes.game_particle import GameParticle
# from srcs.classes.player import Player
from srcs.classes.water_particle_handler import WaterParticleHandler
# from srcs import constants
import pygame


class GameData:
    def __init__(self):
        self.inert_particles: list[GameParticle] = []
        self.player = None  # : Player = Player(constants.MAP_WIDTH // 2, constants.MAP_HEIGHT // 2)
        self.bullets: list[GameParticle] = []
        self.enemies: list[GameParticle] = []
        self.collectibles: list[GameParticle] = []
        self.water_particle_handler: WaterParticleHandler = WaterParticleHandler()
        self.score: int = 0
        self.collectible_spawn_score: int = 0
        self.kills: int = 0
        self.start_ticks = pygame.time.get_ticks()
        self.left_mouse_down = False
        self.right_mouse_down = False
        self.autofire = False
        self.pressed_keys: dict[int, bool] = {k: False for k in range(1000)}
        self.running: bool = True
        self.quit: bool = False
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.current_time = pygame.time.get_ticks()
        self.screen_x = 0
        self.screen_y = 0


    def get_mouse_angle(self):
        mx, my = self.get_mouse_pos()
        px, py = self.player.get_xy()
        return math.atan2(my - py, mx - px)

    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        mx += self.screen_x
        my += self.screen_y
        return mx, my