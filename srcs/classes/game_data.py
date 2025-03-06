import math
from srcs.classes.entity.game_particle import GameParticle
# from srcs.classes.player import Player
# from srcs.classes.water_particle_handler import WaterParticleHandler
from srcs import constants
import pygame


class GameData:
    def __init__(self):
        self.effects: list[GameParticle] = []
        self.player: GameParticle = None  # : Player = Player(constants.MAP_WIDTH // 2, constants.MAP_HEIGHT // 2)
        self.allies: list[GameParticle] = []
        self.enemies: list[GameParticle] = []
        self.collectibles: list[GameParticle] = []
        self.water_particle_handler: 'WaterParticleHandler' = None
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
        self.screen_x = 0  # screen's left position in original map
        self.screen_y = 0  # screen's top position in original map
        self.zoom = 1.0
        self.spawn_ally_timer = 0
        self.spawn_enemy_timer = 0

    def get_mouse_angle(self, unit: GameParticle):
        mx, my = self.get_mouse_pos_in_map()
        px, py = unit.x, unit.y
        return math.atan2(my - py, mx - px)

    def get_mouse_pos_in_map(self):
        mx, my = pygame.mouse.get_pos()
        mx /= self.zoom
        my /= self.zoom
        mx += self.screen_x
        my += self.screen_y

        return mx, my

    def in_screen(self, particle):
        min_x = self.screen_x - particle.rad
        max_x = self.screen_x + constants.SCREEN_WIDTH / self.zoom + particle.rad
        min_y = self.screen_y - particle.rad
        max_y = self.screen_y + constants.SCREEN_HEIGHT / self.zoom + particle.rad
        return min_x < particle.x < max_x and min_y < particle.y < max_y

    def in_map(self, particle):
        min_x = 0 - particle.rad
        max_x = constants.MAP_WIDTH + particle.rad
        min_y = 0 - particle.rad
        max_y = constants.MAP_HEIGHT + particle.rad
        return min_x < particle.x < max_x and min_y < particle.y < max_y

    def get_time_passed(self):
        return self.current_time - self.start_ticks

    def get_player_shield_max_hp(self):
        try:
            return self.player.shield.max_hp
        except AttributeError:
            return 0