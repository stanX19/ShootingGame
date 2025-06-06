from __future__ import annotations

import math
import os
import subprocess
import sys
import traceback


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
from srcs.constants import MAP_WIDTH, MAP_HEIGHT, PLAYER_COLOR, PLAYER_SPEED, \
    ENEMY_COLOR, UNIT_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT
from srcs.classes.faction_data import FactionData
from srcs.unit_classes.advanced_weapons import ALL_ADVANCED_WEAPON_LIST
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum
from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.controller import PlayerController, AIController, BotController, \
    BaseController, SmartAIController
from srcs.classes.entity.unit import Unit
from srcs.unit_classes.basic_unit import BasicLazerUnit, EliteUnit, BasicShootingUnit, RammerUnit, \
    LazerUnit
from srcs.unit_classes.spawner_unit import UnitMothership, MiniMothershipUnit
from srcs.classes.bullet_enemy_collider import collide_enemy_and_bullets
from srcs.classes.collision_handler import repel_collision
from srcs.classes.collectible import *
from srcs.classes.game_data import GameData
from srcs.classes.entity.shield import Shield
from srcs.classes.water_particle_handler import WaterParticleHandler
from srcs.upgrade_pane import UpgradePane

dev_mode = 0
test_mode = 0
god_mode: bool = False

if dev_mode:
    # god_mode = True
    constants.OVERDRIVE_CD = constants.OVERDRIVE_DURATION - 1
    for w in ALL_MAIN_WEAPON_LIST + ALL_SUB_WEAPON_LIST + ALL_ADVANCED_WEAPON_LIST:
        w.level.current_level = w.level.max_level
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

# TODO:
#  add buttons (testing) [Done]
#  remove mothership [Done]
#  add initial enemy spawning mother ships [Done]
#  implement buttons to upgrade player [Done]
#  player can choose three paths: [spawner, turret spawner, attacker]
#  spawner and turret's child will have options to use [weapon, hp, dmg, speed] series upgrade
class Game:
    def __init__(self):
        self.data: GameData = GameData()
        self.throttled_refresh_timer = 0
        self.prev_max_speed = PLAYER_SPEED
        self.prev_controller = SmartAIController()
        self.ally_faction = FactionData(self.data, self.data.allies, self.data.enemies)
        self.enemy_faction = FactionData(self.data, self.data.enemies, self.data.allies)
        self.upgrade_pane = UpgradePane(self.data)
        self.init_game()


    def self_destruct(self):
        self.data.player.kill()

    def init_game(self):
        self.data.zoom = 1.0
        self.data.running = True
        self.data.allies = []
        self.data.enemies = []
        self.data.collectibles = []
        self.ally_faction = FactionData(self.data, self.data.enemies, self.data.allies)
        self.enemy_faction = FactionData(self.data, self.data.allies, self.data.enemies)
        self.data.water_particle_handler = WaterParticleHandler()
        ghost = Unit(self.ally_faction, color=PLAYER_COLOR)
        self.data.player = Unit(self.ally_faction, MAP_WIDTH // 2, MAP_HEIGHT // 4,
                                     color=PLAYER_COLOR, hp=5, shield_hp=2, shield_rad=UNIT_RADIUS * 3, parent=ghost)
        self.data.player.main_weapon.reinit_weapons(MainWeaponEnum.machine_gun)
        self.data.player.sub_weapon.reinit_weapons(MainWeaponEnum.missile)
        if dev_mode:
            self.data.player.score = 10000000
        self.prev_max_speed = self.data.player.speed
        self.prev_controller = self.data.player.controller
        self.data.player.controller = PlayerController()
        self.data.allies.append(self.data.player)

        DISTANCE_FROM_BOUND = 300
        # ghost = Unit(self.ally_faction, color=PLAYER_COLOR)
        ghost = Unit(self.enemy_faction, color=ENEMY_COLOR)
        self.data.enemies.append(UnitMothership(
            self.enemy_faction, MAP_WIDTH - DISTANCE_FROM_BOUND, MAP_HEIGHT - DISTANCE_FROM_BOUND,
            color=ENEMY_COLOR, parent=ghost
        ))
        self.data.enemies.append(UnitMothership(
            self.enemy_faction, DISTANCE_FROM_BOUND, MAP_HEIGHT - DISTANCE_FROM_BOUND,
            color=ENEMY_COLOR, parent=ghost
        ))
        self.data.enemies.append(UnitMothership(
            self.enemy_faction, DISTANCE_FROM_BOUND, DISTANCE_FROM_BOUND,
            color=ENEMY_COLOR, parent=ghost
        ))
        self.data.enemies.append(UnitMothership(
            self.enemy_faction, MAP_WIDTH - DISTANCE_FROM_BOUND, DISTANCE_FROM_BOUND,
            color=ENEMY_COLOR, parent=ghost
        ))
        self.data.enemies.append(UnitMothership(
            self.enemy_faction, MAP_WIDTH // 2, DISTANCE_FROM_BOUND,
            color=ENEMY_COLOR, parent=ghost
        ))
        self.data.enemies.append(UnitMothership(
            self.enemy_faction, MAP_WIDTH // 2, MAP_HEIGHT - DISTANCE_FROM_BOUND,
            color=ENEMY_COLOR, parent=ghost
        ))
        self.data.enemies.append(UnitMothership(
            self.enemy_faction, DISTANCE_FROM_BOUND, MAP_HEIGHT // 2,
            color=ENEMY_COLOR, parent=ghost
        ))
        self.data.enemies.append(UnitMothership(
            self.enemy_faction, MAP_WIDTH - DISTANCE_FROM_BOUND, MAP_HEIGHT // 2,
            color=ENEMY_COLOR, parent=ghost
        ))
        # ghost = Unit(self.ally_faction, color=PLAYER_COLOR)
        # mothership = UnitMothership(
        #     self.ally_faction, MAP_WIDTH // 2, MAP_HEIGHT // 2,
        #     color=PLAYER_COLOR, parent=ghost
        # )
        # mothership.unit_dict = {
        #     BasicShootingUnit: 30,
        #     BasicLazerUnit: 10,
        #     EliteUnit: 3,
        #     RammerUnit: 3,
        # }
        # self.data.allies.append(mothership)

        # self.data.player = UnitMothership(self.data, MAP_WIDTH // 2, MAP_HEIGHT // 2,
        #                                   targets=self.data.enemies, parent_list=self.data.bullets,
        #                                   hp=200, radius=100, dmg=10, color=PLAYER_COLOR, speed=PLAYER_SPEED,
        #                                   child_class=Unit, child_spawn_cd=100,
        #                                   child_kwargs={"hp": 0.01, "dmg": 10, "controller": PlayerDroneController()})

        # self.data.player.main_weapon.reinit_weapons(default_weapons[0])
        # self.data.player.sub_weapon.reinit_weapons(default_weapons[1])
        self.center_focus(lerp_const=1.0)
        self.data.kills = 0
        self.data.autofire = False
        # self.data.player.main_weapon.overdrive_cd = 0.0
        # self.data.player.main_weapon.set_weapon_by_index(0)
        self.data.collectible_spawn_score = 10000
        self.spawn_starter_pack()
        # self.background_update()

    def spawn_starter_pack(self):
        if not test_mode:
            return
        self.data.player.score += 1000000
        self.data.enemies[:] = []
        self.data.allies[:] = []
        # self.data.player = UnitMothership(
        #     self.ally_faction, self.data.player.x - SCREEN_WIDTH // 2 - 300, MAP_HEIGHT // 2,
        #     color=PLAYER_COLOR
        # )
        # self.data.player.unit_dict = {
        #     BasicShootingUnit: 30,
        #     BasicLazerUnit: 10,
        #     EliteUnit: 3,
        #     RammerUnit: 3,
        # }
        self.data.player.score = 100000000000000
        # self.data.player.sub_weapon.reinit_weapons(MainWeaponEnum.swarm)
        self.data.player.main_weapon.reinit_weapons(MainWeaponEnum.fireworks)
        self.data.allies.append(self.data.player)

        # self.data.allies[:] = [self.data.player]
        # self.data.allies.append(
        #     Shield(self.ally_faction, 0, 0, 100, hp=10000000, parent=self.data.player, regen_rate=10000000000))
        self.data.enemies.append(Unit(self.enemy_faction, self.data.player.x + 500, self.data.player.y,
                                              hp=200, dmg=0, weapons=MainWeaponEnum.lazer_mini,
                                              controller=BotController(), variable_shape=True
                                              ))
        self.data.enemies.append(Unit(self.enemy_faction, self.data.player.x - 800, self.data.player.y,
                                      weapons=[],
                                      hp=100000000, dmg=10, radius=300,
                                      # shield_hp=200, shield_rad=300,
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
                if event.key == pygame.K_q and isinstance(self.data.player, Unit):
                    self.data.player.main_weapon.overdrive_start()
                    self.data.player.sub_weapon.overdrive_start()
                if event.key == pygame.K_TAB:
                    self.change_player_unit()
                if event.key == pygame.K_e:
                    self.data.autofire = not self.data.autofire
                if event.key == pygame.K_DELETE:
                    self.self_destruct()
                if event.key == pygame.K_m:
                    if self.upgrade_pane.is_active():
                        self.upgrade_pane.hide()
                    else:
                        self.upgrade_pane.show()
                self.data.pressed_keys[event.key] = True
            elif event.type == pygame.KEYUP:
                self.data.pressed_keys[event.key] = False
            # if event.type == pygame.MOUSEWHEEL:
            #     if event.y > 0:
            #         self.data.zoom *= 1.1
            #     elif event.y < 0 and self.data.player.max_rad * self.data.zoom >= UNIT_RADIUS * 0.75 and self.data.zoom > 0.35:
            #         self.data.zoom /= 1.1
            #     self.center_focus(1.0)
                # if self.data.pressed_keys[pygame.K_TAB]:
                #     self.data.player.sub_weapon.cycle_weapon(- event.y)
                # else:
                #     self.data.player.main_weapon.cycle_weapon(- event.y)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.data.running:
                    self.init_game()
                    self.data.running = True
                if event.button == 1:  # Left mouse button
                    if not self.upgrade_pane.handle_click():
                        self.data.left_mouse_down = True

                elif event.button == 3:  # Right mouse button
                    self.data.right_mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.data.left_mouse_down = False
                    # self.data.player.main_weapon.on_mouse_up()
                elif event.button == 3:  # Right mouse button
                    self.data.right_mouse_down = False

    def _spawn_new_unit(self, faction: FactionData,
                        _constructor: type[Unit],
                        side='top',
                        parent: BaseUnit | None = None,
                        **kwargs):
        unit = _constructor(faction, 0, 0, parent=parent, **kwargs)
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

        faction.parent_list.append(unit)

    def _spawn_units(self, faction: FactionData, color,
                     side='',
                     controller_class: type[BaseController] = AIController,
                     units_dict: dict[type[BaseUnit], int] | None = None,
                     parent: BaseUnit | None = None):
        if test_mode:
            return
        if units_dict is None:
            units_dict = {
                BasicLazerUnit: constants.SPAWN_CAP
            }
        for unit_type, cap in units_dict.items():
            count = len([i for i in faction.parent_list if isinstance(i, unit_type)])
            if count >= cap:
                continue
            self._spawn_new_unit(faction, unit_type, side,
                                 controller=controller_class(),
                                 color=color,
                                 parent=parent)
            break

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
        allies = [i for i in self.data.allies if isinstance(i, Unit)]
        collide_enemy_and_bullets(allies, allies, repel_collision)
        enemies = [i for i in self.data.enemies if isinstance(i, Unit)]
        collide_enemy_and_bullets(enemies, enemies, repel_collision)
        # collide_enemy_and_bullets([self.data.player], self.data.collectibles)
        self.data.water_particle_handler.collide_with_enemies(self.data.enemies)
        self.data.water_particle_handler.collide_with_enemies(self.data.allies)


    def remove_dead_particles(self):
        dead_enemies = [p for p in self.data.enemies if (p.is_dead() and (p.on_death() or True))]
        dead_allies = [p for p in self.data.allies if (p.is_dead() and (p.on_death() or True))]
        dead_effects = [p for p in self.data.effects if (p.is_dead() and (p.on_death() or True))]
        self.data.enemies[:] = [p for p in self.data.enemies if not p.is_dead()]
        self.data.allies[:] = [p for p in self.data.allies if not p.is_dead()]
        self.data.effects[:] = [p for p in self.data.effects if not p.is_dead()]
        #
        # if sum(i for i in self.ally_unit_dict.values()) < constants.SPAWN_CAP:
        #     for p in [p for p in dead_enemies if isinstance(p, BaseUnit)]:
        #         self.ally_unit_dict[type(p)] = 1 + self.ally_unit_dict.get(type(p), 0)
        #         self.enemy_unit_dict[type(p)] = -1 + self.enemy_unit_dict.get(type(p), 0)
        # if sum(i for i in self.enemy_unit_dict.values()) < constants.SPAWN_CAP:
        #     for p in [p for p in dead_allies if isinstance(p, BaseUnit)]:
        #         self.enemy_unit_dict[type(p)] = 1 + self.enemy_unit_dict.get(type(p), 0)
        #         self.ally_unit_dict[type(p)] = -1 + self.ally_unit_dict.get(type(p), 0)

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
        candidates: list[BaseUnit] = [i for i in self.data.allies if
                                      (isinstance(i, BaseUnit)
                                       and i is not original_unit
                                       and self.data.in_map(i))
                                      ]
        candidates.sort(key=lambda x: - x.distance_with(self.data.player) * 0.9)
        try:
            self.data.player = candidates[-1]
        except IndexError:
            return
        if isinstance(original_unit, Unit):
            original_unit.controller = self.prev_controller
        original_unit.max_speed = self.prev_max_speed
        if isinstance(self.data.player, Unit):
            self.prev_controller = self.data.player.controller
        self.prev_max_speed = self.data.player.max_speed
        self.data.player.controller = PlayerController()
        self.data.player.max_speed *= 2


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
        return not any(isinstance(i, BaseUnit) for i in self.data.enemies)

    def check_game_over(self):
        if (any(isinstance(i, BaseUnit) for i in self.data.allies)
                and any(isinstance(i, BaseUnit) for i in self.data.enemies)):
            return
        self.data.running = False

    def center_focus(self, lerp_const=0.1):
        target_screen_x = self.data.player.x - (constants.SCREEN_WIDTH / 2) / self.data.zoom
        target_screen_y = self.data.player.y - (constants.SCREEN_HEIGHT / 2) / self.data.zoom
        self.data.screen_x += (target_screen_x - self.data.screen_x) * lerp_const
        self.data.screen_y += (target_screen_y - self.data.screen_y) * lerp_const

    def refocus_zoom(self, lerp_const=0.05):
        target_zoom = max(0.1, math.sqrt(UNIT_RADIUS / self.data.player.max_rad))
        old_zoom = self.data.zoom
        self.data.zoom += (target_zoom - self.data.zoom) * lerp_const
        x_diff = (constants.SCREEN_WIDTH / old_zoom - constants.SCREEN_WIDTH / self.data.zoom) / 2
        y_diff = (constants.SCREEN_HEIGHT / old_zoom - constants.SCREEN_HEIGHT / self.data.zoom) / 2
        self.data.screen_x += x_diff
        self.data.screen_y += y_diff

    def increment_constants(self):
        TIME_PASSED = self.data.current_time - self.data.start_ticks
        self.data.collectible_spawn_score += TIME_PASSED
        # recover to 100% in 30 secs
        self.data.player.regen_hp(TIME_PASSED / 30000 * self.data.player.max_hp)
        self.data.start_ticks = self.data.current_time
        self.throttled_refresh_timer += 1

    def throttled_refresh(self):
        lst = self.data.enemies + self.data.allies
        if self.throttled_refresh_timer >= len(lst):
            self.throttled_refresh_timer = 0
        # count = 0 | while count < 3 and ...
        while self.throttled_refresh_timer < len(lst):
            e = lst[self.throttled_refresh_timer]
            if isinstance(e, Unit) and e is not self.data.player:
                e.find_new_target()
                return
            self.throttled_refresh_timer += 1

    def update(self):
        self.data.current_time = pygame.time.get_ticks()
        self.increment_constants()
        self.center_focus()
        self.refocus_zoom()
        self.move_everything()
        self.collide_everything()
        self.remove_dead_particles()
        self.throttled_refresh()
        if not self.data.running:
            return
        self.check_player_death()
        self.check_game_over()
        self.upgrade_pane.update_status()

    def add_text_to_screen(self):
        info_str = f"""Score: {self.data.player.score:.0f}
  {int(self.data.player.hp)} / {int(self.data.player.max_hp)} hp
  """.strip()
        # particle count: {len(self.data.water_particle_handler.particles)}
        # buff count: {len(self.data.collectibles)}
        debug_str = f"""\
  fps             : {self.data.clock.get_fps():.0f}
  main weapon     : {self.data.player.main_weapon}
  sub weapon      : {self.data.player.sub_weapon}
  zoom            : {self.data.zoom:.2f}
  enemy count     : {len(self.data.enemies)}
  ally count      : {len(self.data.allies)}
  target          : {self.data.player.target}
  auto fire       : {'on' if self.data.autofire else 'off':4}(E)
  overdrive       : {(self.data.player.main_weapon.overdrive_percentage if isinstance(self.data.player, Unit) else 0) * 100:.0f}% (Q)""".title()
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
        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        self.upgrade_pane.draw(SCREEN)

    def run(self):
        while not self.data.quit:
            self.handle_events()
            self.update()
            self.draw_everything()
            self.data.clock.tick(constants.FPS)
        pygame.quit()


def main():
    # try:
        game = Game()
        game.run()
    # except BaseException:
    #     print(traceback.format_exc())
    #     input("\nPress enter to quit")


if __name__ == '__main__':
    main()
