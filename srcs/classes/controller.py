from __future__ import annotations
import pygame
import math
import random
from typing import Sequence, Optional

from srcs import utils
from srcs.classes.base_unit import BaseUnit
from srcs.classes.shield import Shield
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.bullet import Bullet
from srcs.classes.effect import Effect
from srcs.classes.game_data import GameData
from srcs.classes.draw_utils import draw_arrow


class BaseController:
    """
    A class that alters its own value for reference.
    It does not modify unit.
    """

    def __init__(self):
        self.is_moving: bool = True
        self.move_angle: float = 0.0
        self.aim_angle: float = 0.0
        self.fire_main: bool = False
        self.fire_sub: bool = False

    def update_based_on(self, unit: BaseUnit):
        """Update decision values based on unit state or player input."""
        pass

    def copy(self):
        return self.__class__()


class AIController(BaseController):
    """AI decision-making logic for automated units."""
    def update_based_on(self, unit: BaseUnit):
        if unit.target is None or unit.target.is_dead():
            unit.find_new_target()
        if unit.target:
            self.move_angle = unit.angle_with(unit.target)
            self.aim_angle = AIController.calculate_shoot_angle(unit)
            self.fire_main = unit.distance_with(unit.target) <= unit.shoot_range
            self.fire_sub = unit.distance_with(unit.target) <= unit.shoot_range

    @staticmethod
    def calculate_shoot_angle(unit: BaseUnit):
        # Get the current position and velocity of the target
        target_x, target_y = unit.target.x, unit.target.y
        target_xv, target_yv = unit.target.xv, unit.target.yv

        # Bullet speed (constant)
        bullet_speed = unit.bullet_speed

        # Solve for the lead time: time = distance / relative speed
        # We use an iterative method to find the future point where the bullet can hit
        # it accounts for the fact that the target is moving and the bullet is too.

        lead_time = 0.0
        lead_x = 0
        lead_y = 0

        try:
            # find distance -> find time needed to hit -> predict target location -> repeat
            for _ in range(10):
                lead_x = target_x + target_xv * lead_time
                lead_y = target_y + target_yv * lead_time
                future_distance = math.hypot(lead_x - unit.x, lead_y - unit.y)
                lead_time = future_distance / bullet_speed

            lead_angle = math.atan2(lead_y - unit.y, lead_x - unit.x)
        except ZeroDivisionError:
            lead_angle = unit.angle_with(unit.target)

        return lead_angle


class PlayerController(BaseController):
    """Player control logic for player-controlled units."""
    def update_based_on(self, unit: BaseUnit):
        keys = pygame.key.get_pressed()
        dy, dx = 0, 0
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        self.is_moving = bool(dy or dx)

        self.move_angle = math.atan2(dy, dx)
        self.aim_angle = unit.game_data.get_mouse_angle(unit)
        self.fire_main = unit.game_data.left_mouse_down or unit.game_data.autofire
        self.fire_sub = unit.game_data.right_mouse_down or unit.game_data.autofire

class PlayerDroneController(AIController):
    """non-player control for units that supports player"""
    def update_based_on(self, unit: BaseUnit):
        super().update_based_on(unit)
        affected = unit.distance_with(unit.game_data.player) <= max(SCREEN_WIDTH, SCREEN_HEIGHT) / 2
        if not affected:
            return
        if unit.game_data.left_mouse_down:
            self.aim_angle = unit.game_data.get_mouse_angle(unit)
        self.move_angle = self.aim_angle
        self.fire_main = unit.game_data.left_mouse_down or self.fire_main
        self.fire_sub = unit.game_data.right_mouse_down or self.fire_main