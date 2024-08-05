from __future__ import annotations
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
from srcs.constants import *
from srcs.classes.weapon_handler import WeaponHandler
from srcs.classes.weapons import WeaponType, MainWeaponEnum, SubWeaponEnum
from srcs.classes.missile import Missile
from srcs.classes.bullet import Bullet
from srcs.classes.player import Player
from srcs.classes.enemy import Enemy, EliteEnemy, EnemyMothership
from srcs.classes.water_particle_handler import WaterParticleHandler, WaterParticle
from srcs.classes.bullet_enemy_collider import collide_enemy_and_bullets
from srcs.classes.collectible import *
from srcs.classes.algo import generate_random_point

god_mode: bool = False
start_score: int = 0
default_weapons = ([MainWeaponEnum.machine_gun], [SubWeaponEnum.sub_missile]) #  (MainWeaponEnum, SubWeaponEnum)
# Initialize Pygame
pygame.init()

# Set up the display
MAP_SURFACE = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooting Game")

# Font for score
font = pygame.font.Font(None, 36)
consolas = pygame.font.SysFont("consolas", 16, bold=True, italic=False)


# Game class
class Game:
    def __init__(self):
        self.player: Player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.bullets: list[[Bullet, Missile]] = list([])
        self.enemies: list[Enemy] = list([])
        self.collectibles: list[Collectible] = list([])
        self.water_particle_handler = WaterParticleHandler()
        self.score = start_score
        self.kills = 0
        self.start_ticks = pygame.time.get_ticks()
        self.left_mouse_down = False
        self.right_mouse_down = False
        self.autofire = False
        self.pressed_keys = {k: False for k in range(1000)}
        self.main_weapon = None
        self.sub_weapon = None
        self.running = True
        self.quit = False
        self.clock = pygame.time.Clock()
        self.current_time = pygame.time.get_ticks()
        self.screen_x = 0
        self.screen_y = 0
        self.init_game()

    def init_game(self):
        self.running = True
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.main_weapon = WeaponHandler(self, default_weapons[0])
        self.sub_weapon = WeaponHandler(self, default_weapons[1])
        self.center_focus(lerp_const=1.0)
        self.enemies = list([])
        self.bullets = list([])
        self.collectibles = list([])
        self.water_particle_handler.clear()
        self.score = start_score
        self.kills = 0
        self.autofire = False
        self.main_weapon.overdrive_cd = 0.0
        self.main_weapon.set_weapon_by_index(0)
        self.background_update()

    def background_update(self):
        threshold = min(SCREEN_WIDTH, SCREEN_HEIGHT)
        while not any(e.distance_with(self.player) <= threshold for e in self.enemies):
            self.update()

    def handle_events(self):
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit = True
                if event.key == pygame.K_q:
                    self.main_weapon.overdrive_start()
                if event.key == pygame.K_TAB:
                    self.main_weapon.change_weapon()
                if event.key == pygame.K_e:
                    self.autofire = not self.autofire
                self.pressed_keys[event.key] = True
            elif event.type == pygame.KEYUP:
                self.pressed_keys[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.running:
                    self.init_game()
                    self.running = True
                if event.button == 1:  # Left mouse button
                    self.left_mouse_down = True
                elif event.button == 3:  # Right mouse button
                    self.right_mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.left_mouse_down = False
                    self.main_weapon.on_mouse_up()
                elif event.button == 3:  # Right mouse button
                    self.right_mouse_down = False

    def get_mouse_angle(self):
        mx, my = self.get_mouse_pos()
        px, py = self.player.get_xy()
        return math.atan2(my - py, mx - px)

    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        mx += self.screen_x
        my += self.screen_y
        return mx, my

    def in_screen(self, particle):
        min_x = self.screen_x - particle.rad
        max_x = self.screen_x + SCREEN_WIDTH + particle.rad
        min_y = self.screen_y - particle.rad
        max_y = self.screen_y + SCREEN_HEIGHT + particle.rad
        return min_x < particle.x < max_x and min_y < particle.y < max_y

    def shoot_bullets(self):
        for k in range(49, 58):
            if self.pressed_keys[k]:
                self.main_weapon.change_weapon(k - 49)
                break

        if self.autofire or self.right_mouse_down:
            self.sub_weapon.fire()

        if self.autofire or self.left_mouse_down:
            self.main_weapon.fire()

    def move_player(self):
        dx, dy = 0, 0
        if self.pressed_keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if self.pressed_keys[pygame.K_s]:
            dy += PLAYER_SPEED
        if self.pressed_keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if self.pressed_keys[pygame.K_d]:
            dx += PLAYER_SPEED
        self.player.set_velocity(dx, dy)
        self.player.move()

    def _spawn_new_enemy(self, hp, score, speed, variable_shape, _constructor=Enemy):
        # decide side
        if variable_shape:
            radius = Enemy.get_rad(hp)
        else:
            radius = ENEMY_RADIUS

        side = random.choice(['left', 'right', 'top', 'bottom'])
        if side == 'left':
            ex, ey = -radius, random.randint(0, MAP_HEIGHT)
        elif side == 'right':
            ex, ey = MAP_WIDTH + radius, random.randint(0, MAP_HEIGHT)
        elif side == 'top':
            ex, ey = random.randint(0, MAP_WIDTH), -radius
        elif side == 'bottom':
            ex, ey = random.randint(0, MAP_WIDTH), MAP_HEIGHT + radius
        else:
            ex, ey = -radius, -radius
        self.enemies.append(_constructor(ex, ey, self.player, parent_list=self.enemies, hp=hp,
                                         score=score, speed=speed, variable_shape=variable_shape))

    def get_view_rect(self) -> tuple[int, int, int, int]:
        return self.screen_x, self.screen_y, self.screen_x + SCREEN_WIDTH, self.screen_y + SCREEN_HEIGHT

    def spawn_collectibles(self):
        if len(self.collectibles) >= 300:# or random.random() > 0.005:
            return
        _class = random.choices([HealCollectible, WeaponCollectible, WeaponUpgradeCollectible],
                                [0.10, 0.30, 0.60])[0]
        x, y = generate_random_point(
            rect_small=self.get_view_rect(),
            rect_big=(0, 0, MAP_WIDTH, MAP_HEIGHT),
            padding=COLLECTIBLE_RADIUS
        )
        self.collectibles.append(_class(x, y, self))


    def spawn_enemies(self):
        hp = 1
        score = 100
        speed = ENEMY_SPEED
        if len(self.enemies) < 150 and random.random() < 0.02 + self.score / 100000:
            self._spawn_new_enemy(hp, score, speed, True)
        if len(self.enemies) < 160 and random.random() < min(0.02, (self.score - 150000) / 1000000):
            max_hp = 100
            # distribution of 1/x
            # hp = int(math.e ** (random.uniform(0, 1) * math.log(max_hp, math.e)))
            hp = max_hp
            score = 3000
            speed = ENEMY_SPEED / 4
            self._spawn_new_enemy(hp, score, speed, True, _constructor=EnemyMothership)
        if len(self.enemies) < 170 and random.random() < min(0.04, (self.score - 100000) / 1000000):
            hp = 10
            score = 10000
            speed = PLAYER_SPEED
            self._spawn_new_enemy(hp, score, speed, True, _constructor=EliteEnemy)
            # TODO:
            # can shoot back
        if len(self.enemies) < 180 and random.random() < min(0.01, (self.score - 200000) / 10000000):
            score = 10000
            hp = 200
            speed = PLAYER_SPEED * 0.5
            self._spawn_new_enemy(hp, score, speed, True, _constructor=EnemyMothership)

    def collide_everything(self):
        collide_enemy_and_bullets(self.bullets + [self.player], self.enemies)
        collide_enemy_and_bullets([self.player], self.collectibles)
        self.water_particle_handler.collide_with_enemies(self.enemies)

        for enemy in self.enemies:
            if enemy.hp > 0:
                continue
            enemy.on_death()
            self.score += enemy.score
            self.kills += 1
        self.enemies[:] = [e for e in self.enemies if e.hp > 0]

        self.bullets[:] = [b for b in self.bullets if b.hp > 0]

        for collectible in self.collectibles:
            if collectible.hp <= 0:
                collectible.on_collect()
        self.collectibles[:] = [c for c in self.collectibles if c.hp > 0]

    def move_everything(self):
        for enemy in self.enemies:
            if isinstance(enemy, EliteEnemy):
                enemy.dodge_bullets(self.bullets)
            enemy.move()

        for bullet in self.bullets:
            bullet.move()

        self.bullets[:] = [b for b in self.bullets
                           if not (b.x < 0 or b.x > MAP_WIDTH or b.y < 0 or b.y > MAP_HEIGHT) and b.lifespan > 0]
        self.water_particle_handler.update()
        self.water_particle_handler.remove_out_of_bounds(0, 0, MAP_WIDTH, MAP_HEIGHT)
        self.water_particle_handler.remove_zero_lifespan()
        self.water_particle_handler.remove_zero_hp()
        self.move_player()

    def check_player_death(self):
        if god_mode:
            return
        self.player.hp = max(0, min(PLAYER_HP, self.player.hp))
        if self.player.hp > 0:
            return
        game_over_text = font.render("Game Over", True, (255, 255, 255))
        MAP_SURFACE.blit(game_over_text, (MAP_WIDTH // 2 - 50, MAP_HEIGHT // 2 - 20))
        pygame.display.flip()
        self.running = False

    def center_focus(self, lerp_const=0.1):
        self.screen_x += (self.player.x - SCREEN_WIDTH / 2 - self.screen_x) * lerp_const
        self.screen_y += (self.player.y - SCREEN_HEIGHT / 2 - self.screen_y) * lerp_const

    def update(self):
        if not self.running:
            return
        self.current_time = pygame.time.get_ticks()
        self.score += self.current_time - self.start_ticks
        self.start_ticks = self.current_time
        self.shoot_bullets()
        self.spawn_enemies()
        self.spawn_collectibles()
        self.collide_everything()
        self.check_player_death()
        self.move_everything()
        self.center_focus()

    def add_text_to_screen(self):
        info_str = f"""Score: {self.score}
  {self.main_weapon.index + 1}) {self.main_weapon.name}
  {int(self.player.hp)} / {PLAYER_HP} hp
  """.strip()
        debug_str = f"""\
  fps             : {self.clock.get_fps():.0f}
  weapon level    : {self.main_weapon.weapon.level}
  particle count  : {len(self.water_particle_handler.particles)}
  bullet count    : {len(self.bullets)}
  buff count      : {len(self.collectibles)}
  enemy count     : {len(self.enemies)}
  kills           : {self.kills}
  overdrive cd    : {self.main_weapon.overdrive_cd / 1000:<4.1f}(Q)
  auto fire       : {'on' if self.autofire else 'off':4}(E)""".title()
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
        MAP_SURFACE.fill(BACKGROUND_COLOR)
        self.player.draw(MAP_SURFACE)

        # particles
        def draw_particles(particles: [GameParticle]):
            for particle in particles:
                if not self.in_screen(particle):
                    continue
                particle.draw(MAP_SURFACE)

        draw_particles(self.collectibles)
        draw_particles(self.bullets)
        draw_particles(self.enemies)

        self.water_particle_handler.draw_everything(MAP_SURFACE, (self.screen_x, self.screen_y))

        SCREEN.fill((100, 100, 100))
        SCREEN.blit(MAP_SURFACE, (-self.screen_x, -self.screen_y))
        self.add_text_to_screen()

        pygame.display.flip()

    def run(self):
        while not self.quit:
            self.handle_events()
            self.update()
            self.draw_everything()
            self.clock.tick(FPS)
        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
