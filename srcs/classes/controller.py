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
        self.move_angle: float = 0.0
        self.aim_angle: float = 0.0
        self.fire_main: bool = False
        self.fire_sub: bool = False

    def update_based_on(self, unit: BaseUnit):
        """Update decision values based on unit state or player input."""
        pass


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
        if keys[pygame.K_w]:
            self.move_angle = 0
        elif keys[pygame.K_s]:
            self.move_angle = math.pi
        elif keys[pygame.K_a]:
            self.move_angle = math.pi * 1.5
        elif keys[pygame.K_d]:
            self.move_angle = math.pi / 2

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.aim_angle = math.atan2(mouse_y - unit.y, mouse_x - unit.x)
        self.fire_main = pygame.mouse.get_pressed()[0]
        self.fire_sub = pygame.mouse.get_pressed()[2]