from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
try:
    import pygame
    import numpy
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy'])
    import pygame
    import numpy
from srcs.constants import BULLET_SPEED, UNIT_SHOOT_RANGE, MAP_WIDTH, MAP_HEIGHT, PLAYER_COLOR, PLAYER_SPEED, \
    BULLET_COLOR, ENEMY_COLOR
from srcs.classes.weapons import MainWeaponEnum
from srcs.classes.base_unit import BaseUnit
from srcs.classes.controller import PlayerController, PlayerDroneController, AIController, BotController, \
    BaseController, SmartAIController
from srcs.classes.unit import Unit, ShootingUnit, ShieldedUnit
from srcs.classes.unit_classes import BasicShootingUnit, EliteUnit, SuperShootingUnit, UnitMiniMothership, SniperUnit, UnitMothership
from srcs.classes.bullet_enemy_collider import collide_enemy_and_bullets
from srcs.classes.collectible import *
from srcs.classes.game_data import GameData
from srcs.classes.shield import Shield
from srcs.classes.water_particle_handler import WaterParticleHandler

dev_mode = 0
test_mode = 0
god_mode: bool = False
# default_weapons = ([MainWeaponEnum.machine_gun], [SubWeaponEnum.sub_missile])
if dev_mode:
    god_mode = True
    constants.OVERDRIVE_CD = constants.OVERDRIVE_DURATION - 1
    for w in ALL_MAIN_WEAPON_LIST + ALL_SUB_WEAPON_LIST:
        w.level = w.max_lvl
    # default_weapons = (ALL_MAIN_WEAPON_LIST, ALL_SUB_WEAPON_LIST)
# Initialize Pygame
pygame.init()

# Set up the display
MAP_SURFACE = pygame.Surface((constants.MAP_WIDTH, constants.MAP_HEIGHT), pygame.SRCALPHA)
SCREEN = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Space Shooting Game")

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 180)
consolas = pygame.font.SysFont("consolas", 16, bold=True, italic=False)


# Game class
class Game:
    def __init__(self):
        self.data: GameData = GameData()
        self.throttled_refresh_timer = 0
        self.prev_max_speed = PLAYER_SPEED
        self.prev_controller = SmartAIController()
        self.init_game()

    def init_game(self):
        self.data.running = True
        self.data.allies = []
        self.data.enemies = []
        self.data.collectibles = []
        self.data.water_particle_handler = WaterParticleHandler()
        self.data.ally_mothership = UnitMothership(
            self.data, MAP_WIDTH / 2, MAP_HEIGHT - 100,
            self.data.enemies, self.data.allies,
            color=PLAYER_COLOR
        )
        self.data.enemy_mothership = UnitMothership(
            self.data, MAP_WIDTH / 2, 100,
            self.data.allies, self.data.enemies,
            color=ENEMY_COLOR
        )
        self.data.allies.append(self.data.ally_mothership)
        self.data.enemies.append(self.data.enemy_mothership)
        self.data.player = EliteUnit(self.data, MAP_WIDTH // 2, MAP_HEIGHT // 2,
                                     targets=self.data.enemies, parent_list=self.data.allies,
                                     color=PLAYER_COLOR)
        if test_mode:
            self.data.player.weapon_handler.reinit_weapons(MainWeaponEnum.lazer)

        # self.data.player = UnitMothership(self.data, MAP_WIDTH // 2, MAP_HEIGHT // 2,
        #                                   targets=self.data.enemies, parent_list=self.data.bullets,
        #                                   hp=200, radius=100, dmg=10, color=PLAYER_COLOR, speed=PLAYER_SPEED,
        #                                   child_class=ShootingUnit, child_spawn_cd=100,
        #                                   child_kwargs={"hp": 0.01, "dmg": 10, "controller": PlayerDroneController()})
        self.data.player.controller = PlayerController()
        self.data.allies.append(self.data.player)
        # self.data.player.main_weapon.reinit_weapons(default_weapons[0])
        # self.data.player.sub_weapon.reinit_weapons(default_weapons[1])
        self.center_focus(lerp_const=1.0)
        self.data.kills = 0
        self.data.autofire = False
        # self.data.player.main_weapon.overdrive_cd = 0.0
        # self.data.player.main_weapon.set_weapon_by_index(0)
        self.data.collectible_spawn_score = 10000
        self.spawn_starter_pack()
        self.background_update()

    def spawn_starter_pack(self):
        if not test_mode:
            return
        self.data.allies.append(
            Shield(self.data, 0, 0, 100, hp=10000000, parent=self.data.player, regen_rate=10000000000))
        self.data.enemies.append(ShootingUnit(self.data, self.data.player.x + 500, self.data.player.y,
                                              self.data.allies, self.data.enemies,
                                              hp=200, dmg=10000, weapons=MainWeaponEnum.lazer_mini,
                                              controller=BotController(), variable_shape=True
                                              ))
        # self.data.bullets.append(Shield(self.data, self.data.player.x, self.data.player.y, hp=50, dmg=1,
        #                                 rad=self.data.player.rad + 50, parent=self.data.player, regen_rate=10))
        # self.spawn_collectible_at(self.data.player.x - 90, self.data.player.y - 40)
        # self.spawn_collectible_at(self.data.player.x - 100, self.data.player.y)
        # self.spawn_collectible_at(self.data.player.x - 90, self.data.player.y + 40)

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
                # if event.key == pygame.K_q:
                #     self.data.player.main_weapon.overdrive_start()
                if event.key == pygame.K_TAB:
                    self.change_player_unit()
                if event.key == pygame.K_e:
                    self.data.autofire = not self.data.autofire
                self.data.pressed_keys[event.key] = True
            elif event.type == pygame.KEYUP:
                self.data.pressed_keys[event.key] = False
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.data.zoom *= 1.1
                elif event.y < 0 and self.data.zoom >= 0.1:
                    self.data.zoom /= 1.1
                self.center_focus(1.0)
                # if self.data.pressed_keys[pygame.K_TAB]:
                #     self.data.player.sub_weapon.cycle_weapon(- event.y)
                # else:
                #     self.data.player.main_weapon.cycle_weapon(- event.y)
            if event.type == pygame.MOUSEBUTTONDOWN:
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
                    # self.data.player.main_weapon.on_mouse_up()
                elif event.button == 3:  # Right mouse button
                    self.data.right_mouse_down = False

    def _spawn_new_unit(self, _constructor: type[Unit],
                        target_list: Optional[list[GameParticle]],
                        parent_list: Optional[list[GameParticle]],
                        side='top', **kwargs):
        if parent_list is None:
            parent_list = self.data.enemies
        if target_list is None:
            target_list = self.data.allies
        unit = _constructor(self.data, 0, 0, target_list, parent_list, **kwargs)
        spawn_rad = unit.rad + 300

        # side = random.choice(['left', 'right', 'top', 'bottom'])
        if 'left' in side:
            unit.x = -spawn_rad
        elif 'right' in side:
            unit.x = constants.MAP_WIDTH + spawn_rad
        else:
            unit.x = random.randint(spawn_rad, constants.MAP_WIDTH - spawn_rad)
        if 'top' in side:
            unit.y = -spawn_rad
        elif 'bot' in side:
            unit.y = constants.MAP_HEIGHT + spawn_rad
        else:
            unit.y = random.randint(spawn_rad, constants.MAP_HEIGHT - spawn_rad)

        parent_list.append(unit)

    def _spawn_units(self, color,
                     target_list: Optional[list[GameParticle]],
                     parent_list: Optional[list[GameParticle]],
                     side='',
                     controller_class: type[BaseController] = AIController):
        if test_mode:
            return
        BASE_CAP = constants.SPAWN_CAP
        units_dict = {
            SniperUnit: 1,
            SuperShootingUnit: 3,
            EliteUnit: 5,
            BasicShootingUnit: BASE_CAP,
        }
        for unit_type, cap in units_dict.items():
            count = len([i for i in parent_list if isinstance(i, unit_type)])
            if count >= cap:
                continue
            self._spawn_new_unit(unit_type, target_list, parent_list, side,
                                 controller=controller_class(),
                                 color=color)
            break
        # # if len(parent_list) < BASE_CAP + 20 and random.random() < min(0.01, (self.data.score - 40000) / 50000000):
        # #     score = min(40000, 20000 + self.data.score // 1000)
        # #     hp = 100  # + 150 * min(1.0, score / 100000)
        # #     speed = constants.UNIT_SPEED * 1.5
        # #     self._spawn_new_unit(hp, score, speed, True, _constructor=ShootingUnit, dmg=10,
        # #                          radius=60 + constants.UNIT_RADIUS, weapons=MainWeaponEnum.missile,
        # #                          color=color, parent_list=parent_list, target_list=target_list, side=side,
        # #                          controller=controller_class())
        #
        # elif len(
        #         parent_list) < BASE_CAP + 2:  # and random.random() < min(0.02, (self.data.score - 60000) / 10000000):
        #     hp = 20
        #     score = 600
        #     speed = constants.UNIT_SPEED * 2.5
        #     self._spawn_new_unit(hp, score, speed, True, _constructor=ShootingUnit, dmg=10,
        #                          shoot_range=UNIT_SHOOT_RANGE * 1.5,
        #                          color=color, parent_list=parent_list, target_list=target_list, side=side,
        #                          controller=controller_class(), weapons=MainWeaponEnum.lazer_mini)
        #
        # elif len(
        #         parent_list) < BASE_CAP + 3:  # and random.random() < min(0.01, (self.data.score - 100000) / 100000000):
        #     score = min(40000, 20000 + self.data.score // 1000)
        #     hp = 300  # + 150 * min(1.0, score / 100000)
        #     speed = constants.UNIT_SPEED * 1.5
        #     self._spawn_new_unit(hp, score, speed, True, _constructor=UnitMothership, dmg=10,
        #                          radius=100, shield_rad=200, bullet_speed=BULLET_SPEED * 1.5,
        #                          shoot_range=UNIT_SHOOT_RANGE * 1.5,
        #                          child_class=ShootingUnit, weapons=MainWeaponEnum.lazer,
        #                          child_speed=(speed * 5, speed * 10),
        #                          child_kwargs={
        #                              "hp": 1, "dmg": 10, "weapons": MainWeaponEnum.piercing_machine_gun
        #                          },
        #                          color=color, parent_list=parent_list, target_list=target_list, side=side,
        #                          controller=controller_class())

    def spawn_enemies(self):
        if self.data.enemy_mothership.is_dead():
            return
        self.data.spawn_enemy_timer -= 1
        if self.data.spawn_enemy_timer > 0:
            return
        self.data.spawn_enemy_timer = constants.SPAWN_CD
        self._spawn_units(color=constants.ENEMY_COLOR, parent_list=self.data.enemies,
                          target_list=self.data.allies, side='top')

    def spawn_allies(self):
        if self.data.ally_mothership.is_dead():
            return
        self.data.spawn_ally_timer -= 1
        if self.data.spawn_ally_timer > 0:
            return
        self.data.spawn_ally_timer = constants.SPAWN_CD
        self._spawn_units(color=constants.PLAYER_COLOR, parent_list=self.data.allies,
                          target_list=self.data.enemies, side='bot',
                          controller_class=SmartAIController)

    def get_view_rect(self) -> tuple[int, int, int, int]:
        return self.data.screen_x, self.data.screen_y, self.data.screen_x + constants.SCREEN_WIDTH, self.data.screen_y + constants.SCREEN_HEIGHT

    #
    # def spawn_collectible_at(self, x: Optional[float] = None, y: Optional[float] = None):
    #     # MIN_ON_MAP = 10
    #     # MAX_ON_MAP = 50
    #     # if len(self.data.collectibles) > MIN_ON_MAP and random.random() > 0.0002 * (MAX_ON_MAP - len(self.data.collectibles)):
    #     #     return
    #     all_main_weapon = len(ALL_MAIN_WEAPON_LIST)
    #     all_sub_weapon = len(ALL_SUB_WEAPON_LIST)
    #     main_weapon_obtained = len(self.data.player.main_weapon.all_weapons)
    #     sub_weapon_obtained = len(self.data.player.sub_weapon.all_weapons)
    #     not_obtained_main_weapons = all_main_weapon - main_weapon_obtained
    #     not_obtained_sub_weapons = all_sub_weapon - sub_weapon_obtained
    #     maxed_main_weapons = len([i for i in self.data.player.main_weapon.all_weapons if i.is_max_lvl()])
    #     maxed_sub_weapons = len([i for i in self.data.player.sub_weapon.all_weapons if i.is_max_lvl()])
    #     missing_hp = self.data.player.max_hp - self.data.player.hp
    #     collectibles = [
    #                         HealCollectible,
    #                         MainWeaponCollectible,
    #                         SubWeaponCollectible,
    #                         WeaponUpgradeCollectible,
    #                         SubWeaponUpgradeCollectible,
    #                    ]
    #     probabilities = [max(0, i) for i in [
    #                         missing_hp + 3,
    #                         not_obtained_main_weapons,
    #                         not_obtained_sub_weapons,
    #                         (all_main_weapon - maxed_main_weapons) * 2 + 2,
    #                         (all_sub_weapon - maxed_sub_weapons) * 2,
    #                     ]]
    #     _class = random.choices(collectibles, probabilities)[0]
    #     if x is None or y is None:
    #         x, y = generate_random_point(
    #             rect_small=self.get_view_rect(),
    #             rect_big=(0, 0, constants.MAP_WIDTH, constants.MAP_HEIGHT),
    #             padding=constants.COLLECTIBLE_RADIUS
    #         )
    #     self.data.collectibles.append(_class(x, y, self.data))

    def collide_everything(self):
        collide_enemy_and_bullets(self.data.allies, self.data.enemies)
        # collide_enemy_and_bullets([self.data.player], self.data.collectibles)
        self.data.water_particle_handler.collide_with_enemies(self.data.enemies)
        self.data.water_particle_handler.collide_with_enemies(self.data.allies)


    def remove_dead_particles(self):
        self.data.enemies[:] = [p for p in self.data.enemies if not (p.is_dead() and not p.on_death())]
        self.data.allies[:] = [p for p in self.data.allies if not (p.is_dead() and not p.on_death())]
        self.data.effects[:] = [p for p in self.data.effects if not (p.is_dead() and not p.on_death())]

        for collectible in self.data.collectibles:
            if collectible.is_dead() and isinstance(collectible, Collectible):
                collectible.on_collect()
        self.data.collectibles[:] = [c for c in self.data.collectibles if not c.is_dead()]

    def move_everything(self):
        for effect in self.data.effects:
            effect.move()
        for ally in self.data.allies:
            ally.move()
        for enemy in self.data.enemies:
            enemy.move()

        self.data.water_particle_handler.update()
        self.data.water_particle_handler.remove_out_of_bounds(0, 0, constants.MAP_WIDTH, constants.MAP_HEIGHT)
        self.data.water_particle_handler.remove_zero_lifespan()
        self.data.water_particle_handler.remove_zero_hp()
        # self.move_player()

    def change_player_unit(self):
        original_unit = self.data.player
        candidates: list[BaseUnit] = [i for i in self.data.allies if isinstance(i,
                                                                                BaseUnit) and i is not original_unit and i is not self.data.ally_mothership]
        candidates.sort(key=lambda x: x.hp - x.distance_with(self.data.player) / 7.5)
        try:
            self.data.player = candidates[-1]
        except IndexError:
            return
        original_unit.controller = self.prev_controller
        original_unit.max_speed = self.prev_max_speed
        self.prev_controller = self.data.player.controller
        self.prev_max_speed = self.data.player.max_speed
        self.data.player.controller = PlayerController()
        self.data.player.max_speed = PLAYER_SPEED

    def check_player_death(self):
        self.data.player.hp = max(0.0, min(self.data.player.max_hp, self.data.player.hp))
        if not self.data.player.is_dead():
            return
        if god_mode:
            self.data.player.hp = max(0.01, self.data.player.hp)
            if self.data.player not in self.data.allies:
                self.data.allies.append(self.data.player)
        if self.data.player.is_dead():
            self.change_player_unit()

    def is_victory(self):
        return not self.data.enemies

    def check_game_over(self):
        if self.data.allies and self.data.enemies:
            return
        self.data.running = False

    def center_focus(self, lerp_const=0.1):
        self.data.screen_x += (self.data.player.x - constants.SCREEN_WIDTH / 2 / self.data.zoom - self.data.screen_x) * lerp_const
        self.data.screen_y += (self.data.player.y - constants.SCREEN_HEIGHT / 2 / self.data.zoom - self.data.screen_y) * lerp_const

    def increment_constants(self):
        TIME_PASSED = self.data.current_time - self.data.start_ticks
        self.data.collectible_spawn_score += TIME_PASSED
        # recover to 100% in 30 secs
        self.data.player.hp = min(self.data.player.max_hp, self.data.player.hp + TIME_PASSED / 30000 * self.data.player.max_hp)
        self.data.start_ticks = self.data.current_time
        self.throttled_refresh_timer += 1

    def throttled_refresh(self):
        lst = self.data.enemies + self.data.allies
        if self.throttled_refresh_timer >= len(lst):
            self.throttled_refresh_timer = 0
        # count = 0 | while count < 3 and ...
        while self.throttled_refresh_timer < len(lst):
            e = lst[self.throttled_refresh_timer]
            if isinstance(e, Unit):
                e.find_new_target()
                return
            self.throttled_refresh_timer += 1

    def update(self):
        self.data.current_time = pygame.time.get_ticks()
        self.increment_constants()
        self.center_focus()
        self.move_everything()
        self.collide_everything()
        self.remove_dead_particles()
        if not self.data.running:
            return
        self.throttled_refresh()
        self.check_player_death()
        self.check_game_over()
        self.spawn_enemies()
        self.spawn_allies()

    def add_text_to_screen(self):
        info_str = f"""Score: {self.data.player.score}
  {int(self.data.player.hp)} / {int(self.data.player.max_hp)} hp
  """.strip()
        debug_str = f"""\
  fps             : {self.data.clock.get_fps():.0f}
  zoom            : {self.data.zoom:.2f}
  particle count  : {len(self.data.water_particle_handler.particles)}
  buff count      : {len(self.data.collectibles)}
  enemy count     : {len(self.data.enemies)}
  ally count      : {len(self.data.allies)}
  kills           : {self.data.kills}
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

        if self.data.running:
            return
        text = "Victory" if self.is_victory() else "Defeat"
        game_over_text = big_font.render(text, True, (255, 255, 255))
        SCREEN.blit(game_over_text, (
            (constants.SCREEN_WIDTH - game_over_text.get_width()) // 2,
            (constants.SCREEN_HEIGHT - game_over_text.get_height()) // 2
        ))

    def draw_everything(self):
        MAP_SURFACE.fill(constants.BACKGROUND_COLOR)
        self.data.player.draw(MAP_SURFACE)

        # Particles
        def draw_particles(particles: [GameParticle]):
            for particle in sorted(particles, key=lambda p: p.rad):
                if not self.data.in_screen(particle):
                    continue
                particle.draw(MAP_SURFACE)

        draw_particles(self.data.collectibles)
        draw_particles(self.data.allies)
        draw_particles(self.data.enemies)
        draw_particles(self.data.effects)

        self.data.water_particle_handler.draw_everything(MAP_SURFACE, (self.data.screen_x, self.data.screen_y))

        if self.data.zoom < 0.5:
            scaled_map = pygame.transform.scale(
                MAP_SURFACE,
                (int(MAP_WIDTH * self.data.zoom), int(MAP_HEIGHT * self.data.zoom))
            )
            SCREEN.fill((100, 100, 100))
            SCREEN.blit(scaled_map, (-self.data.screen_x * self.data.zoom, -self.data.screen_y * self.data.zoom))
        else:
            visible_rect = pygame.Rect(
                self.data.screen_x,
                self.data.screen_y,
                SCREEN.get_width() / self.data.zoom,
                SCREEN.get_height() / self.data.zoom,
            )

            # Create a new surface for the visible area
            cropped_map = pygame.Surface((visible_rect.width, visible_rect.height))
            cropped_map.fill((100, 100, 100))  # Fill with the background color

            # Determine the area of MAP_SURFACE to blit onto the new surface
            map_rect = MAP_SURFACE.get_rect()
            intersect_rect = visible_rect.clip(map_rect)
            if intersect_rect.width > 0 and intersect_rect.height > 0:
                cropped_map.blit(
                    MAP_SURFACE,
                    (intersect_rect.x - visible_rect.x, intersect_rect.y - visible_rect.y),
                    intersect_rect
                )
            scaled_cropped_map = pygame.transform.scale(cropped_map, (SCREEN.get_width(), SCREEN.get_height()))
            SCREEN.fill((100, 100, 100))
            SCREEN.blit(scaled_cropped_map, (0, 0))

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
