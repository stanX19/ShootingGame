from __future__ import annotations

import math
import random

import pygame

from srcs.classes.entity.base_unit import BaseUnit
from srcs.constants import *


class BaseController:
    """
    A class that alters its own value for reference.
    It does not modify unit.
    """

    def __init__(self):
        self._turn_direction = random.choice((-math.pi / 2, math.pi / 2))
        self._prev_hp: int = 0
        self._retreat: int = 0  # frames to retreat
        self.is_moving: bool = True
        self.move_angle: float = 0.0
        self.aim_x: float = 0.0
        self.aim_y: float = 0.0
        self.fire_main: bool = False
        self.fire_sub: bool = False

    def update_based_on(self, unit: BaseUnit):
        """Update decision values based on unit state or player input."""
        pass

    def copy(self):
        return self.__class__()

    def get_child(self):
        return self.copy()


class BotController(BaseController):
    def update_based_on(self, unit: BaseUnit):
        self.is_moving = False
        self.fire_main = True
        self.fire_sub = True

class AIController(BaseController):
    def update_based_on(self, unit: BaseUnit):
        super().update_based_on(unit)
        if unit.target is None or unit.target.is_dead():
            unit.find_new_target()
        if unit.target:
            self.move_angle = unit.angle_with(unit.target)
            self.aim_x, self.aim_y = AIController.calculate_shoot_coordinate(unit)
            self.fire_main = unit.distance_with(unit.target) <= unit.shoot_range
            self.fire_sub = unit.distance_with(unit.target) <= unit.shoot_range

    @staticmethod
    def calculate_shoot_coordinate(unit: BaseUnit) -> tuple[float, float]:
        target_x, target_y = unit.target.x, unit.target.y
        target_xv, target_yv = unit.target.xv, unit.target.yv

        bullet_speed = unit.bullet_speed

        lead_time = 0.0
        lead_x = target_x
        lead_y = target_y

        try:
            for _ in range(10):
                lead_x = target_x + target_xv * lead_time
                lead_y = target_y + target_yv * lead_time
                future_distance = math.hypot(lead_x - unit.x, lead_y - unit.y)
                lead_time = future_distance / bullet_speed

            return lead_x, lead_y
        except ZeroDivisionError:
            return target_x, target_y

    @staticmethod
    def calculate_shoot_angle(unit: BaseUnit):
        aim_x, aim_y = AIController.calculate_shoot_coordinate(unit)
        return unit.angle_with_cord(aim_x, aim_y)


class SmartAIController(AIController):
    """AI decision-making logic for automated units."""

    def update_based_on(self, unit: BaseUnit):
        super().update_based_on(unit)
        if self._prev_hp > unit.hp:
            self._retreat = 4 * FPS
        if self._retreat > 0:
            self._retreat -= 1
            self.move_angle += math.pi
            unit.find_new_target()
            if unit.is_targeting_self(unit.target):
                self.fire_sub = self.fire_main = True
        elif unit.distance_with(unit.target) <= unit.shoot_range:
            self.move_angle += self._turn_direction
        self._prev_hp = unit.hp


class PlayerDroneController(SmartAIController):
    """non-player control for units that supports player"""

    def update_based_on(self, unit: BaseUnit):
        super().update_based_on(unit)
        affected = unit.faction.game_data.in_screen(unit)
        if not affected:
            return
        if unit.faction.game_data.left_mouse_down:
            self.aim_x, self.aim_y = unit.faction.game_data.get_mouse_pos()
        self.move_angle = unit.angle_with_cord(self.aim_x, self.aim_y)
        self.fire_main = unit.faction.game_data.left_mouse_down or self.fire_main
        self.fire_sub = unit.faction.game_data.right_mouse_down or self.fire_main


class PlayerController(AIController):
    """Player control logic for player-controlled units."""

    def update_based_on(self, unit: BaseUnit):
        self._update_using_ai(unit)
        self._update_movement(unit)
        self.fire_main = unit.faction.game_data.left_mouse_down or unit.faction.game_data.autofire
        self.fire_sub = unit.faction.game_data.right_mouse_down or unit.faction.game_data.autofire

    def _update_movement(self, unit:BaseUnit):
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

    def _update_using_ai(self, unit: BaseUnit):
        self.aim_x, self.aim_y = unit.faction.game_data.get_mouse_pos()
        closest_unit = None
        closest_distance = float('inf')
        is_unit = False
        for target in unit.faction.target_list:
            distance = target.distance_with_cord(self.aim_x, self.aim_y)
            if is_unit and not isinstance(target, BaseUnit):
                continue
            if distance < closest_distance:
                closest_unit = target
                closest_distance = distance
                is_unit = isinstance(target, BaseUnit)
        if closest_distance < 25 / unit.faction.game_data.zoom:
            unit.target = closest_unit
            super().update_based_on(unit)

    def get_child(self):
        return PlayerDroneController()

class AIDroneController(SmartAIController):
    def update_based_on(self, unit: BaseUnit):
        if isinstance(unit.parent, BaseUnit):
            unit.target = unit.parent.target
        super().update_based_on(unit)