import math
import random
import subprocess
import sys
import os
from constants import *
from weapon_handler import WeaponHandler
from weapons import WeaponType, WeaponEnum
from missile import Missile
from bullet import Bullet
from player import Player
from enemy import Enemy
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
try:
    import pygame
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
    import pygame

god_mode = True
start_score = 100000000
# Initialize Pygame
pygame.init()

# Set up the display
MAP_SURFACE = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooting Game")

# Font for score
font = pygame.font.Font(None, 36)


# Game class
class Game:
    def __init__(self):
        self.player: Player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.bullets: list[[Bullet, Missile]] = []
        self.enemies: list[Enemy] = []
        self.score = start_score
        self.start_ticks = pygame.time.get_ticks()
        self.left_mouse_down = False
        self.right_mouse_down = False
        self.autofire = False
        self.pressed_keys = {k: False for k in range(1000)}
        self.main_weapon = WeaponHandler(self)
        self.sub_weapon = WeaponHandler(self, [
            WeaponType("sub missile", 2000, MISSILE_SPEED, 8, min_bullet_count=2, growth_factor=50000, bullet_class="missile")
        ])
        self.running = True
        self.quit = False
        self.clock = pygame.time.Clock()
        self.current_time = pygame.time.get_ticks()
        self.init_game()
        self.focus_x = self.player.x
        self.focus_y = self.player.x

    def init_game(self):
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.enemies = []
        self.bullets = []
        self.bullets = []
        self.score = start_score
        self.autofire = False

    def handle_events(self):
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit = False
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
                elif event.button == 3:  # Right mouse button
                    self.right_mouse_down = False

    def get_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        mx -= self.focus_x
        my -= self.focus_y
        return mx, my

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

    def _spawn_new_enemy(self, hp, score, speed, variable_shape):
        # decide side
        radius = Enemy.get_rad(hp)

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
        self.enemies.append(Enemy(ex, ey, hp=hp, score=score, speed=speed, variable_shape=variable_shape))

    def spawn_enemies(self):
        hp = 1
        score = 100
        speed = ENEMY_SPEED
        variable_shape = True
        if len(self.enemies) < 100 and random.random() < 0.02 + self.score / 1000000:
            self._spawn_new_enemy(hp, score, speed, True)
        if len(self.enemies) < 110 and random.random() < min(0.01, (self.score - 100000) / 1000000):
            max_hp = 100
            # distribution of 1/x
            # hp = int(math.e ** (random.uniform(0, 1) * math.log(max_hp, math.e)))
            hp = max_hp
            score = 1000
            speed = ENEMY_SPEED / 2
            self._spawn_new_enemy(hp, score, speed, True)
        if len(self.enemies) < 120 and random.random() < min(0.01, (self.score - 150000) / 10000000):
            hp = 10
            score = 500
            speed = PLAYER_SPEED
            self._spawn_new_enemy(hp, score, speed, True)
        if len(self.enemies) < 130 and random.random() < min(0.001, (self.score - 200000) / 100000000):
            hp = 10000
            score = 1000000
            speed = ENEMY_SPEED / 4
            self._spawn_new_enemy(hp, score, speed, True)

    def handle_collision(self, bullet: Bullet, enemy: Enemy):
        enemy.hp -= bullet.dmg
        bullet.hp -= bullet.dmg + enemy.hp
        if bullet.hp <= 0 and bullet in self.bullets:
            self.bullets.remove(bullet)

    def check_collision_with_enemies(self, bullet, start_idx):
        for enemy in self.enemies[start_idx:]:
            if enemy.x + enemy.rad < bullet.x - bullet.rad:
                start_idx += 1
                continue
            break
        for enemy in self.enemies[start_idx:]:
            if enemy.x - enemy.rad > bullet.x + bullet.rad:
                break
            if math.hypot(enemy.x - bullet.x, enemy.y - bullet.y) < enemy.rad + bullet.rad:
                self.handle_collision(bullet, enemy)
        return start_idx

    def collide_everything(self):
        self.bullets.sort(key=lambda b: b.x - b.rad)
        self.enemies.sort(key=lambda b: b.x - b.rad)

        enemy_start_idx = 0
        for bullet in self.bullets[:]:
            enemy_start_idx = self.check_collision_with_enemies(bullet, enemy_start_idx)
            if enemy_start_idx >= len(self.enemies):
                break

        for enemy in self.enemies[:]:
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
                self.score += enemy.score
                continue

    def move_everything(self):
        for enemy in self.enemies:
            enemy.move_towards_player(self.player)

        for bullet in self.bullets[:]:
            bullet.move()
            if bullet not in self.bullets:
                continue
            elif bullet.x < 0 or bullet.x > MAP_WIDTH or bullet.y < 0 or bullet.y > MAP_HEIGHT:
                self.bullets.remove(bullet)
            elif bullet.lifespan <= 0.0:
                self.bullets.remove(bullet)

        self.move_player()

    def check_player_death(self):
        if god_mode:
            return
        for enemy in self.enemies:
            if math.hypot(enemy.x - self.player.x, enemy.y - self.player.y) < enemy.rad + self.player.rad:
                game_over_text = font.render("Game Over", True, (255, 255, 255))
                MAP_SURFACE.blit(game_over_text, (MAP_WIDTH // 2 - 50, MAP_HEIGHT // 2 - 20))
                pygame.display.flip()
                self.running = False
                break

    def center_focus(self):
        LERP_CONST = 0.1
        self.focus_x += (SCREEN_WIDTH // 2 - self.player.x - self.focus_x) * LERP_CONST
        self.focus_y += (SCREEN_HEIGHT // 2 - self.player.y - self.focus_y) * LERP_CONST

    def update(self):
        if not self.running:
            return
        self.current_time = pygame.time.get_ticks()
        self.score += self.current_time - self.start_ticks
        self.start_ticks = self.current_time
        self.shoot_bullets()
        self.spawn_enemies()
        self.collide_everything()
        self.check_player_death()
        self.move_everything()
        self.center_focus()

    def add_text_to_screen(self):
        info_str = f"""Score: {self.score}
  {self.main_weapon.index}) {self.main_weapon.name}"""
        y = 10
        for line in info_str.split("\n"):
            text = font.render(line, True, (255, 255, 255))
            SCREEN.blit(text, (10, y))
            y += font.get_height() + 10

    def draw(self):
        MAP_SURFACE.fill(BACKGROUND_COLOR)
        self.player.draw(MAP_SURFACE)
        for bullet in self.bullets:
            bullet.draw(MAP_SURFACE)
        for enemy in self.enemies:
            enemy.draw(MAP_SURFACE)

        SCREEN.fill((100, 100, 100))
        SCREEN.blit(MAP_SURFACE, (self.focus_x, self.focus_y))
        self.add_text_to_screen()

        pygame.display.flip()

    def run(self):
        while not self.quit:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(30)
        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
