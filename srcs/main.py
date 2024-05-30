import math
import random
import subprocess
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
try:
	import pygame
except ImportError:
	subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
import utils

god_mode = False
start_score = 0
# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1520
SCREEN_HEIGHT = 800
MAP_WIDTH = 2000
MAP_HEIGHT = 2000
PLAYER_RADIUS = 5
BULLET_RADIUS = 2
MISSILE_RADIUS = 3
ENEMY_RADIUS = 10
PLAYER_COLOR = (255, 255, 0)  # Yellow
BULLET_COLOR = (255, 255, 255)  # White
MISSILE_COLOR = (0, 255, 0)  # Green
ENEMY_COLOR = (255, 105, 180)  # Pink
BACKGROUND_COLOR = (0, 0, 0)  # Black
PLAYER_SPEED = 5
BULLET_SPEED = 10.0
MISSILE_SPEED = 8
ENEMY_SPEED = 2

# Set up the display
MAP_SURFACE = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooting Game")

# Font for score
font = pygame.font.Font(None, 36)


class WeaponType:
    def __init__(self, name, reload, velocity=BULLET_SPEED, count=None, radius=BULLET_RADIUS,
                 recoil=0, hp=1.0, dmg=1.0, spread=math.pi * 0.8,
                 min_bullet_count=1, growth_factor=0.0, offset_factor=1.0):
        self.name = name
        self.shot_delay = reload
        self.speed = velocity
        if count is None:
            count = int(reload * 0.01) + 1
        self.bullet_count = count
        self.rad = radius
        self.recoil = recoil
        self.hp = hp
        self.dmg = dmg
        self.spread = spread
        self.min_bullet_count = min_bullet_count
        self.growth_factor = growth_factor
        self.offset_factor = offset_factor

    def __str__(self):
        return self.name

    pass


class WeaponEnum:
    machine_gun = WeaponType("machine gun", reload=100, velocity=10, count=10, radius=2, growth_factor=50000,
                             offset_factor=0.1)
    lazer = WeaponType("lazer", reload=200, velocity=100, count=100, radius=1)
    shotgun = WeaponType("shotgun", reload=1000, velocity=50, count=100, radius=1,
                         recoil=PLAYER_SPEED, dmg=1, min_bullet_count=10, growth_factor=1000)
    bomb = WeaponType("bomb", reload=500, velocity=5, count=1, radius=25, recoil=25, hp=10000, dmg=10)
    missile = WeaponType("missile", 500, count=10, growth_factor=50000)
    shield = WeaponType("shield", reload=10000, velocity=1, count=200, hp=500, radius=1,
                        dmg=1 / ENEMY_RADIUS * ENEMY_SPEED, spread=2*math.pi,
                        min_bullet_count=30, growth_factor=5000)


# Player class
class Player:
    def __init__(self, x, y, rad=PLAYER_RADIUS):
        self.x = x
        self.y = y
        self.xv = 0
        self.yv = 0
        self.rad = rad

    def draw(self):
        pygame.draw.circle(MAP_SURFACE, PLAYER_COLOR, (self.x, self.y), self.rad)

    def move(self):
        self.x += self.xv
        self.y += self.yv
        self.x = utils.normalize(self.x, self.rad, MAP_WIDTH - self.rad)
        self.y = utils.normalize(self.y, self.rad, MAP_HEIGHT - self.rad)

    def set_velocity(self, dx, dy):
        self.xv = dx
        self.yv = dy

    def recoil(self, shooting_angle, magnitude):
        self.x -= math.cos(shooting_angle) * magnitude
        self.y -= math.sin(shooting_angle) * magnitude


# Enemy class
class Enemy:
    def __init__(self, x, y, radius=ENEMY_RADIUS, speed=ENEMY_SPEED, color=ENEMY_COLOR, hp=1, score=100):
        self.x = x
        self.y = y
        self.xv = 0
        self.yv = 0
        self.rad = radius
        self.color = color
        self.hp = hp
        self.score = score
        self.speed = speed

    def draw(self):
        pygame.draw.circle(MAP_SURFACE, self.color, (self.x, self.y), self.rad)

    def move_towards_player(self, player):
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.xv = self.speed * math.cos(angle)
        self.yv = self.speed * math.sin(angle)
        self.x += self.xv
        self.y += self.yv

    def update_appearance_based_on_hp(self):
        self.rad = ENEMY_RADIUS + self.hp - 1
        self.color = utils.color_norm((255, 105 - self.hp, 180 - self.hp))


# Bullet class
class Bullet:
    def __init__(self, x, y, angle, speed=None, rad=None, weapon=None, hp=1, dmg=1):
        self.x = x
        self.y = y
        if isinstance(weapon, WeaponType):
            if speed is None:
                speed = weapon.speed
            if rad is None:
                rad = weapon.rad
            if hp == 1:
                hp = weapon.hp
            if dmg == 1:
                dmg = weapon.dmg
        self.xv = speed * math.cos(angle)
        self.yv = speed * math.sin(angle)
        self.speed = speed
        self.rad = rad
        self.hp = hp
        self.dmg = dmg

    def draw(self):
        pygame.draw.circle(MAP_SURFACE, BULLET_COLOR, (int(self.x), int(self.y)), self.rad)

    def move(self):
        self.x += self.xv
        self.y += self.yv


# Missile class
class Missile:
    def __init__(self, x, y, angle, target: [Enemy, None] = None, radius=MISSILE_RADIUS,
                 speed=MISSILE_SPEED, lifespan=60 * 3, hp=1, dmg=10):
        self.x = x
        self.y = y
        self.xv = math.cos(angle) * PLAYER_SPEED
        self.yv = math.sin(angle) * PLAYER_SPEED
        self.rad = radius
        self.angle = angle
        self.lifespan = lifespan  # fps * seconds
        self.target = target
        self.reached_target = False
        self.hp = hp
        self.dmg = dmg
        self.speed = speed

    def draw(self):
        pygame.draw.circle(MAP_SURFACE, MISSILE_COLOR, (int(self.x), int(self.y)), self.rad)

    def find_target(self):
        search_radius = 200
        hypot = math.hypot(self.xv, self.yv)
        dy = self.yv * search_radius / hypot
        dx = self.xv * search_radius / hypot
        self.target = Missile.find_target_at(self.x + dx, self.y + dy, search_radius)

    @staticmethod
    def find_target_at(x, y, search_radius=100.0):
        lowest_distance = search_radius
        target = None
        for enemy in game.enemies:
            y_dis = enemy.y - y
            x_dis = enemy.x - x
            distance = math.hypot(x_dis, y_dis)
            if distance < lowest_distance + enemy.rad:
                lowest_distance = distance
                target = enemy
        return target

    def angle_with(self, other):
        try:
            y_dis = other.y - self.y
            x_dis = other.x - self.x
            return self.angle - math.atan2(y_dis, x_dis)
        except AttributeError:
            return 0

    def calculate_intercept_angle(self, target):
        tx = target.x
        ty = target.y
        tvx = target.xv
        tvy = target.yv
        dx = tx - self.x
        dy = ty - self.y
        target_speed = math.hypot(tvx, tvy)
        a = target_speed ** 2 - (self.speed * 0.1) ** 2
        b = 2 * (dx * tvx + dy * tvy)
        c = dx ** 2 + dy ** 2
        disc = b ** 2 - 4 * a * c

        if disc < 0:
            return math.atan2(dy, dx)
        t1 = (-b + math.sqrt(disc)) / (2 * a)
        t2 = (-b - math.sqrt(disc)) / (2 * a)
        t = min(t1, t2) if t1 > 0 and t2 > 0 else max(t1, t2, 0)
        intercept_x = tx + tvx * t
        intercept_y = ty + tvy * t
        return math.atan2(intercept_y - self.y, intercept_x - self.x)

    def update(self):
        if self.target not in game.enemies:
            self.find_target()
        if self.lifespan <= 0:
            self.explode()
        if isinstance(self.target, Enemy):
            target_angle = self.calculate_intercept_angle(self.target)
            angle_diff = utils.angle_diff(target_angle, self.angle)
            angle_diff = utils.normalize(angle_diff, -math.pi / 24, math.pi / 24)
            self.angle += angle_diff
        self.xv = self.speed * math.cos(self.angle)
        self.yv = self.speed * math.sin(self.angle)
        magnitude = math.hypot(self.xv, self.yv)
        if magnitude > self.speed:
            self.xv = self.xv / magnitude * self.speed
            self.yv = self.yv / magnitude * self.speed

    def move(self):
        self.update()
        self.x += self.xv
        self.y += self.yv
        self.lifespan -= 1

    def explode(self):
        game.bullets.remove(self)


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
        self.weapon = WeaponEnum.machine_gun
        self.all_weapon = [attr for attr in vars(WeaponEnum).values() if isinstance(attr, WeaponType)]
        self.last_shot_time = {weapon: -1000000 for weapon in self.all_weapon}
        self.missile_delay = 2000  # Milliseconds between shots
        self.last_missile_time = 0
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
        self.weapon = WeaponEnum.machine_gun
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
                    cur_idx = (self.all_weapon.index(self.weapon) + 1) % len(self.all_weapon)
                    self.weapon = self.all_weapon[cur_idx]
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
        new_weapon = self.weapon
        for k in range(49, 58):
            if self.pressed_keys[k]:
                new_weapon = self.all_weapon[(k - 49) % len(self.all_weapon)]
        if self.weapon != new_weapon:
            self.weapon = new_weapon

        mx, my = self.get_mouse_pos()
        dy, dx = my - self.player.y, mx - self.player.x
        hypot = math.hypot(dy, dx)
        angle = math.atan2(dy, dx)

        # sub weapon
        if (self.autofire or self.right_mouse_down) and self.current_time - self.last_missile_time > self.missile_delay:
            bullet_count = int(utils.normalize(self.score / WeaponEnum.machine_gun.growth_factor, 2, 8))
            target = Missile.find_target_at(mx, my)
            missile_angle = angle + math.pi / 2
            for _ in range(bullet_count):  # Shoot missiles in all directions
                self.bullets.append(Missile(self.player.x, self.player.y, missile_angle, target))
                missile_angle += math.pi * 2 / bullet_count
            self.last_missile_time = self.current_time

        # main weapon
        if not (self.autofire or self.left_mouse_down)\
                or self.current_time - self.last_shot_time[self.weapon] < self.weapon.shot_delay:
            return
        self.last_shot_time[self.weapon] = self.current_time

        if self.weapon.growth_factor != 0:
            bullet_count = int(self.score / self.weapon.growth_factor)
            bullet_count = utils.normalize(bullet_count, self.weapon.min_bullet_count, self.weapon.bullet_count)
        else:
            bullet_count = self.weapon.bullet_count

        if self.weapon is WeaponEnum.lazer:
            lazer_dy = dy / hypot * BULLET_RADIUS
            lazer_dx = dx / hypot * BULLET_RADIUS
            for i in range(bullet_count):
                self.bullets.append(Bullet(
                        self.player.x + lazer_dx * i,
                        self.player.y + lazer_dy * i,
                        angle,
                        weapon=self.weapon
                    ))

        elif self.weapon is WeaponEnum.shotgun:
            direction_count = bullet_count
            angle_offset = math.pi * 0.4 / direction_count
            for i in range(bullet_count):
                offset = (i % direction_count - (direction_count - 1) / 2) * angle_offset
                shoot_angle = angle + offset
                speed = random.uniform(self.weapon.speed / 2, self.weapon.speed)
                self.bullets.append(
                    Bullet(
                        self.player.x,
                        self.player.y,
                        shoot_angle,
                        speed=speed,
                        weapon=self.weapon
                    ))

        elif self.weapon is WeaponEnum.missile:
            direction_count = bullet_count
            angle_offset = math.pi * 2 / direction_count
            target = Missile.find_target_at(mx, my)
            for i in range(bullet_count):
                offset = (i % direction_count - (direction_count - 1) / 2) * angle_offset
                shoot_angle = angle + offset
                self.bullets.append(Missile(self.player.x, self.player.y, shoot_angle, target))

        else:
            angle_offset = self.weapon.spread / bullet_count  # Adjust this value to control spread
            for i in range(bullet_count):
                offset = (i - (bullet_count - 1) / 2) * angle_offset
                shoot_angle = angle + offset
                bullet_angle = angle + offset * self.weapon.offset_factor
                dy, dx = math.sin(shoot_angle) * self.player.rad * 5, math.cos(shoot_angle) * self.player.rad * 5
                dy, dx = dy - math.sin(angle) * self.player.rad * 5, dx - math.cos(angle) * self.player.rad * 5
                self.bullets.append(Bullet(self.player.x + dx, self.player.y + dy, bullet_angle, weapon=self.weapon))

        self.player.recoil(angle, self.weapon.recoil)

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

    def spawn_enemies(self):
        side = random.choice(['left', 'right', 'top', 'bottom'])
        if side == 'left':
            ex, ey = 0, random.randint(0, MAP_HEIGHT)
        elif side == 'right':
            ex, ey = MAP_WIDTH, random.randint(0, MAP_HEIGHT)
        elif side == 'top':
            ex, ey = random.randint(0, MAP_WIDTH), 0
        elif side == 'bottom':
            ex, ey = random.randint(0, MAP_WIDTH), MAP_HEIGHT
        else:
            ex, ey = 0, 0
        if len(self.enemies) < 200 and random.random() < 0.02 + self.score / 1000000:
            self.enemies.append(Enemy(ex, ey))
        if self.score > 50000 and random.random() < min(0.04, self.score / 10000000):
            max_hp = 100
            # distribution of 1/x
            # hp = int(math.e ** (random.uniform(0, 1) * math.log(max_hp, math.e)))
            hp = max_hp
            radius = ENEMY_RADIUS + hp - 1
            score = hp * 1000
            color = utils.color_norm((255, 105 - hp, 180 - hp))
            self.enemies.append(Enemy(ex, ey, hp=hp, radius=radius, color=color, score=score))

    def collide_everything(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies:
                if math.hypot(enemy.x - bullet.x, enemy.y - bullet.y) < enemy.rad + bullet.rad:
                    enemy.hp -= bullet.dmg
                    bullet.hp -= bullet.dmg + enemy.hp
                    enemy.update_appearance_based_on_hp()
                    break
            if bullet.hp <= 0:
                self.bullets.remove(bullet)

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
            if bullet.x < 0 or bullet.x > MAP_WIDTH or bullet.y < 0 or bullet.y > MAP_HEIGHT:
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
  {self.all_weapon.index(self.weapon) + 1}) {self.weapon}"""
        y = 10
        for line in info_str.split("\n"):
            text = font.render(line, True, (255, 255, 255))
            SCREEN.blit(text, (10, y))
            y += font.get_height() + 10

    def draw(self):
        MAP_SURFACE.fill(BACKGROUND_COLOR)
        self.player.draw()
        for bullet in self.bullets:
            bullet.draw()
        for enemy in self.enemies:
            enemy.draw()

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


game = Game()
game.run()
