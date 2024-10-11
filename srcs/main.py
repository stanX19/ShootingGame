from __future__ import annotations
from typing import Optional
import math
import random
import subprocess
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
try:
    import pygame
    import numpy
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy'])
    import pygame
    import numpy
from srcs import constants
from srcs.classes.weapon_handler import WeaponHandler
from srcs.classes.weapons import WeaponType, MainWeaponEnum, SubWeaponEnum, ALL_MAIN_WEAPON_LIST, ALL_SUB_WEAPON_LIST
from srcs.classes.missile import Missile
from srcs.classes.bullet import Bullet
from srcs.classes.player import Player
from srcs.classes.enemy import Enemy, EliteEnemy, EnemyMothership, DodgingEnemy
from srcs.classes.water_particle_handler import WaterParticleHandler, WaterParticle
from srcs.classes.bullet_enemy_collider import collide_enemy_and_bullets
from srcs.classes.collectible import *
from srcs.classes.algo import generate_random_point
from srcs.classes.game_data import GameData

dev_mode = 1
god_mode: bool = False
start_score: int = 0
default_weapons = ([MainWeaponEnum.machine_gun], [SubWeaponEnum.sub_missile])
if dev_mode:
    god_mode = True
    start_score = 10000000000
    constants.OVERDRIVE_CD = constants.OVERDRIVE_DURATION - 1
    for w in ALL_MAIN_WEAPON_LIST + ALL_SUB_WEAPON_LIST:
        w.level = w.max_lvl
    default_weapons = (ALL_MAIN_WEAPON_LIST, ALL_SUB_WEAPON_LIST)
# Initialize Pygame
pygame.init()

# Set up the display
MAP_SURFACE = pygame.Surface((constants.MAP_WIDTH, constants.MAP_HEIGHT), pygame.SRCALPHA)
SCREEN = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooting Game")

# Font for score
font = pygame.font.Font(None, 36)
consolas = pygame.font.SysFont("consolas", 16, bold=True, italic=False)


# Game class
class Game:
    def __init__(self):
        self.data: GameData = GameData()
        self.init_game()

    def init_game(self):
        self.data.running = True
        self.data.player = Player(self.data, constants.MAP_WIDTH // 2, constants.MAP_HEIGHT // 2)
        self.data.player.main_weapon.reinit_weapons(default_weapons[0])
        self.data.player.sub_weapon.reinit_weapons(default_weapons[1])
        self.center_focus(lerp_const=1.0)
        self.data.enemies = []
        self.data.bullets = []
        self.data.collectibles = []
        self.data.water_particle_handler.clear()
        self.data.score = start_score
        self.data.kills = 0
        self.data.autofire = False
        self.data.player.main_weapon.overdrive_cd = 0.0
        self.data.player.main_weapon.set_weapon_by_index(0)
        self.data.collectible_spawn_score = 10000
        self.background_update()
        self.spawn_starter_pack()

    def spawn_starter_pack(self):
        self.spawn_collectible_at(self.data.player.x - 90, self.data.player.y - 40)
        self.spawn_collectible_at(self.data.player.x - 100, self.data.player.y)
        self.spawn_collectible_at(self.data.player.x - 90, self.data.player.y + 40)

    def background_update(self):
        threshold = min(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        while not any(e.distance_with(self.data.player) <= threshold for e in self.data.enemies):
            self.update()

    def handle_events(self):
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.data.quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.data.quit = True
                if event.key == pygame.K_q:
                    self.data.player.main_weapon.overdrive_start()
                if event.key == pygame.K_TAB:
                    self.data.player.sub_weapon.change_weapon()
                if event.key == pygame.K_e:
                    self.data.autofire = not self.data.autofire
                self.data.pressed_keys[event.key] = True
            elif event.type == pygame.KEYUP:
                self.data.pressed_keys[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.data.running:
                    self.init_game()
                    self.data.running = True
                if event.button == 1:  # Left mouse button
                    self.data.left_mouse_down = True
                elif event.button == 3:  # Right mouse button
                    self.data.right_mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.data.left_mouse_down = False
                    self.data.player.main_weapon.on_mouse_up()
                elif event.button == 3:  # Right mouse button
                    self.data.right_mouse_down = False

    def shoot_bullets(self):
        for k in range(49, 58):
            if self.data.pressed_keys[k]:
                self.data.player.main_weapon.change_weapon(k - 49)
                break

        if self.data.autofire or self.data.right_mouse_down:
            self.data.player.sub_weapon.fire()

        if self.data.autofire or self.data.left_mouse_down:
            self.data.player.main_weapon.fire()

    def move_player(self):
        dx, dy = 0, 0
        if self.data.pressed_keys[pygame.K_w]:
            dy -= constants.PLAYER_SPEED
        if self.data.pressed_keys[pygame.K_s]:
            dy += constants.PLAYER_SPEED
        if self.data.pressed_keys[pygame.K_a]:
            dx -= constants.PLAYER_SPEED
        if self.data.pressed_keys[pygame.K_d]:
            dx += constants.PLAYER_SPEED
        self.data.player.set_velocity(dx, dy)
        self.data.player.move()

    def _spawn_new_enemy(self, hp, score, speed, variable_shape, _constructor=Enemy,
                         radius=constants.ENEMY_RADIUS, **kwargs):
        # decide side
        if variable_shape:
            radius = Enemy.get_rad(hp, hp, radius)

        side = random.choice(['left', 'right', 'top', 'bottom'])
        if side == 'left':
            ex, ey = -radius, random.randint(0, constants.MAP_HEIGHT)
        elif side == 'right':
            ex, ey = constants.MAP_WIDTH + radius, random.randint(0, constants.MAP_HEIGHT)
        elif side == 'top':
            ex, ey = random.randint(0, constants.MAP_WIDTH), -radius
        elif side == 'bottom':
            ex, ey = random.randint(0, constants.MAP_WIDTH), constants.MAP_HEIGHT + radius
        else:
            ex, ey = -radius, -radius
        self.data.enemies.append(_constructor(self.data, ex, ey, self.data.player, parent_list=self.data.enemies, hp=hp,
                                              score=score, speed=speed, variable_shape=variable_shape, radius=radius,
                                              **kwargs))

    def spawn_enemies(self):
        hp = 1
        score = 100
        speed = constants.ENEMY_SPEED
        if len(self.data.enemies) < 150 and random.random() < 0.02 + self.data.score / 100000:
            self._spawn_new_enemy(hp, score, speed, True)
        if len(self.data.enemies) < 160 and random.random() < min(0.02, (self.data.score - 10000) / 10000000):
            hp = 10
            score = 300
            speed = constants.PLAYER_SPEED
            self._spawn_new_enemy(hp, score, speed, True, _constructor=EliteEnemy)
        if len(self.data.enemies) < 170 and random.random() < min(0.01, (self.data.score - 20000) / 10000000):
            score = min(40000, 20000 + self.data.score // 1000)
            hp = 100  # + 150 * min(1.0, score / 100000)
            speed = constants.PLAYER_SPEED * 0.5
            self._spawn_new_enemy(hp, score, speed, True, _constructor=EnemyMothership, dmg=0.1,
                                  radius=60 + constants.ENEMY_RADIUS)
        # if len(self.data.enemies) < 175 and random.random() < min(0.005, self.data.score / 100000):
        #     hp = 50
        #     score = 1000
        #     speed = constants.ENEMY_SPEED / 2
        #     self._spawn_new_enemy(hp, score, speed, True, _constructor=Enemy, radius=30, dmg=5)


    def get_view_rect(self) -> tuple[int, int, int, int]:
        return self.data.screen_x, self.data.screen_y, self.data.screen_x + constants.SCREEN_WIDTH, self.data.screen_y + constants.SCREEN_HEIGHT

    def spawn_collectible_at(self, x: Optional[float] = None, y: Optional[float] = None):
        # MIN_ON_MAP = 10
        # MAX_ON_MAP = 50
        # if len(self.data.collectibles) > MIN_ON_MAP and random.random() > 0.0002 * (MAX_ON_MAP - len(self.data.collectibles)):
        #     return
        all_main_weapon = len(ALL_MAIN_WEAPON_LIST)
        all_sub_weapon = len(ALL_SUB_WEAPON_LIST)
        main_weapon_obtained = len(self.data.player.main_weapon.all_weapon)
        sub_weapon_obtained = len(self.data.player.sub_weapon.all_weapon)
        not_obtained_main_weapons = all_main_weapon - main_weapon_obtained
        not_obtained_sub_weapons = all_sub_weapon - sub_weapon_obtained
        maxed_main_weapons = len([i for i in self.data.player.main_weapon.all_weapon if i.is_max_lvl()])
        maxed_sub_weapons = len([i for i in self.data.player.sub_weapon.all_weapon if i.is_max_lvl()])
        missing_hp = self.data.player.max_hp - self.data.player.hp
        collectibles = [
                            HealCollectible,
                            MainWeaponCollectible,
                            SubWeaponCollectible,
                            WeaponUpgradeCollectible,
                            SubWeaponUpgradeCollectible,
                       ]
        probabilities = [max(0, i) for i in [
                            missing_hp + 3,
                            not_obtained_main_weapons,
                            not_obtained_sub_weapons,
                            (all_main_weapon - maxed_main_weapons) * 2 + 2,
                            (all_sub_weapon - maxed_sub_weapons) * 2,
                        ]]
        _class = random.choices(collectibles, probabilities)[0]
        if x is None or y is None:
            x, y = generate_random_point(
                rect_small=self.get_view_rect(),
                rect_big=(0, 0, constants.MAP_WIDTH, constants.MAP_HEIGHT),
                padding=constants.COLLECTIBLE_RADIUS
            )
        self.data.collectibles.append(_class(x, y, self.data))


    def collide_everything(self):
        collide_enemy_and_bullets(self.data.bullets + [self.data.player], self.data.enemies)
        collide_enemy_and_bullets([self.data.player], self.data.collectibles)
        self.data.water_particle_handler.collide_with_enemies(self.data.enemies)

        for enemy in self.data.enemies:
            if not enemy.is_dead():
                continue
            self.data.collectible_spawn_score += enemy.score
            #                                                   60 seconds per drop
            if random.random() < self.data.collectible_spawn_score / 60000 - len(self.data.collectibles) / 50:
                self.spawn_collectible_at(enemy.x, enemy.y)
                self.data.collectible_spawn_score = 0
            self.data.score += enemy.score
            self.data.kills += 1

    def remove_dead_particles(self):
        self.data.enemies[:] = [p for p in self.data.enemies if not (p.is_dead() and not p.on_death())]
        self.data.bullets[:] = [p for p in self.data.bullets if not (p.is_dead() and not p.on_death())]
        self.data.effects[:] = [p for p in self.data.effects if not (p.is_dead() and not p.on_death())]

        for collectible in self.data.collectibles:
            if collectible.is_dead() and isinstance(collectible, Collectible):
                collectible.on_collect()
        self.data.collectibles[:] = [c for c in self.data.collectibles if not c.is_dead()]

    def move_everything(self):
        for enemy in self.data.enemies:
            if isinstance(enemy, DodgingEnemy):
                enemy.dodge_bullets(self.data.bullets)
            enemy.move()

        for bullet in self.data.bullets:
            bullet.move()

        for effect in self.data.effects:
            effect.move()

        self.data.bullets[:] = [b for b in self.data.bullets if not b.is_dead()]
        self.data.water_particle_handler.update()
        self.data.water_particle_handler.remove_out_of_bounds(0, 0, constants.MAP_WIDTH, constants.MAP_HEIGHT)
        self.data.water_particle_handler.remove_zero_lifespan()
        self.data.water_particle_handler.remove_zero_hp()
        self.move_player()

    def check_player_death(self):
        if god_mode:
            self.data.player.hp = max(0.01, self.data.player.hp)
            return
        self.data.player.hp = max(0.0, min(self.data.player.max_hp, self.data.player.hp))
        if not self.data.player.is_dead():
            return
        game_over_text = font.render("Game Over", True, (255, 255, 255))
        MAP_SURFACE.blit(game_over_text, (constants.MAP_WIDTH // 2 - 50, constants.MAP_HEIGHT // 2 - 20))
        pygame.display.flip()
        self.data.running = False

    def center_focus(self, lerp_const=0.1):
        self.data.screen_x += (self.data.player.x - constants.SCREEN_WIDTH / 2 - self.data.screen_x) * lerp_const
        self.data.screen_y += (self.data.player.y - constants.SCREEN_HEIGHT / 2 - self.data.screen_y) * lerp_const

    def increment_constants(self):
        TIME_PASSED = self.data.current_time - self.data.start_ticks
        self.data.score += TIME_PASSED
        self.data.collectible_spawn_score += TIME_PASSED
        # recover to 10 in one minute
        self.data.player.hp = min(self.data.player.max_hp, self.data.player.hp + TIME_PASSED / 60000 * 10)
        self.data.start_ticks = self.data.current_time


    def update(self):
        if not self.data.running:
            return
        self.data.current_time = pygame.time.get_ticks()
        self.collide_everything()
        self.remove_dead_particles()
        self.move_everything()
        self.check_player_death()
        self.shoot_bullets()
        self.spawn_enemies()
        self.center_focus()

    def add_text_to_screen(self):
        info_str = f"""Score: {self.data.score}
  {self.data.player.main_weapon.index + 1}) {self.data.player.main_weapon.name}
  {int(self.data.player.hp)} / {int(self.data.player.max_hp)} hp
  """.strip()
        debug_str = f"""\
  fps             : {self.data.clock.get_fps():.0f}
  main weapon     : {self.data.player.main_weapon.name:20} (lvl {self.data.player.main_weapon.level_str})
  sub weapon      : {self.data.player.sub_weapon.name:20} (lvl {self.data.player.sub_weapon.level_str})
  particle count  : {len(self.data.water_particle_handler.particles)}
  bullet count    : {len(self.data.bullets)}
  buff count      : {len(self.data.collectibles)}
  enemy count     : {len(self.data.enemies)}
  kills           : {self.data.kills}
  overdrive       : {(1.0 - self.data.player.main_weapon.overdrive_cd / constants.OVERDRIVE_CD) * 100:.0f}% (Q)
  auto fire       : {'on' if self.data.autofire else 'off':4}(E)""".title()
        y = 10
        for line in info_str.split("\n"):
            text = font.render(line, True, (255, 255, 255))
            SCREEN.blit(text, (10, y))
            y += text.get_height() + 10
        for line in debug_str.split("\n"):
            text = consolas.render(line, True, (255, 255, 255))
            SCREEN.blit(text, (10, y))
            y += text.get_height()

    def draw_everything(self):
        MAP_SURFACE.fill(constants.BACKGROUND_COLOR)
        self.data.player.draw(MAP_SURFACE)

        # particles
        def draw_particles(particles: [GameParticle]):
            for particle in sorted(particles, key=lambda p: p.rad):
                if not self.data.in_screen(particle):
                    continue
                particle.draw(MAP_SURFACE)

        draw_particles(self.data.collectibles)
        draw_particles(self.data.bullets)
        draw_particles(self.data.enemies)
        draw_particles(self.data.effects)

        self.data.water_particle_handler.draw_everything(MAP_SURFACE, (self.data.screen_x, self.data.screen_y))

        SCREEN.fill((100, 100, 100))
        SCREEN.blit(MAP_SURFACE, (-self.data.screen_x, -self.data.screen_y))
        self.add_text_to_screen()

        pygame.display.flip()

    def run(self):
        while not self.data.quit:
            self.handle_events()
            self.update()
            self.draw_everything()
            self.data.clock.tick(constants.FPS)
        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
