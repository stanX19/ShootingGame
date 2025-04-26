from __future__ import annotations

import math
from typing import Callable, Any

from srcs.classes import algo
from srcs.classes.entity.breakable import Breakable
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.entity.lazer import Lazer
from collections import defaultdict
from typing import Sequence


from srcs.classes.collision_handler import CollisionHandlerType, damaging_collision


def is_colliding(a: GameParticle, b: GameParticle):
    if isinstance(a, Lazer) and isinstance(b, Lazer):
        # return algo.line_line_distance(a.x, a.y, a.end_x, a.end_y, b.x, b.y, b.end_x,
        #                                b.end_y) < a.rad + b.rad
        return False
    elif isinstance(a, Lazer):
        return algo.line_point_distance(a.prev_x, a.prev_y, a.end_x, a.end_y, b.x, b.y) < a.rad + b.rad
    elif isinstance(b, Lazer):
        return algo.line_point_distance(b.prev_x, b.prev_y, b.end_x, b.end_y, a.x, a.y) < a.rad + b.rad
    else:
        return a.distance_with(b) < 0

def assign_to_cells(particles: Sequence[GameParticle], cell_size: float) -> dict:
    """
    Assigns particles to grid cells based on their positions.
    """
    cells = defaultdict(list)
    for particle in particles:
        cell_x = int(particle.x // cell_size)
        cell_y = int(particle.y // cell_size)
        cells[(cell_x, cell_y)].append(particle)
    return cells


def get_neighboring_cells(cell_x: int, cell_y: int) -> list:
    """
    Returns the coordinates of a cell and its eight neighbors.
    """
    return [
        (cell_x + dx, cell_y + dy)
        for dx in range(-1, 2)
        for dy in range(-1, 2)
    ]


def check_collision_within_cells(bullets: Sequence[GameParticle], enemies: Sequence[GameParticle], cell_size: float):
    """
    Detects collisions between bullets and enemies using cell-based spatial partitioning.
    """
    # Step 1: Assign bullets and enemies to cells
    bullet_cells = assign_to_cells(bullets, cell_size)
    enemy_cells = assign_to_cells(enemies, cell_size)

    # Step 2: Check collisions within the relevant cells
    for (cell_x, cell_y), cell_bullets in bullet_cells.items():
        # Get all enemies in this cell and neighboring cells
        possible_enemies = []
        for neighbor in get_neighboring_cells(cell_x, cell_y):
            possible_enemies.extend(enemy_cells.get(neighbor, []))

        # Check collisions between bullets and these enemies
        for bullet in cell_bullets:
            for enemy in possible_enemies:
                if is_colliding(bullet, enemy):
                    damaging_collision(bullet, enemy)

def check_collision_with_enemies(bullet: GameParticle, enemies: list[GameParticle], start_idx: int,
                                 collision_handler:CollisionHandlerType = damaging_collision):
    for enemy in enemies[start_idx:]:
        if enemy.x + enemy.get_collision_rad() < bullet.x - bullet.get_collision_rad():
            start_idx += 1
            continue
        break
    for enemy in enemies[start_idx:]:
        if enemy.x - enemy.get_collision_rad() > bullet.x + bullet.get_collision_rad():
            break
        if is_colliding(bullet, enemy):
            collision_handler(bullet, enemy)
    return start_idx


def _collide_sorted_enemy_and_bullets(bullets: list[GameParticle], enemies: list[GameParticle],
                                      collision_handler:CollisionHandlerType = damaging_collision):
    enemy_start_idx = 0
    for bullet in bullets:
        enemy_start_idx = check_collision_with_enemies(bullet, enemies, enemy_start_idx, collision_handler)
        if enemy_start_idx >= len(enemies):
            break


def collide_enemy_and_bullets(bullets: Sequence[GameParticle], enemies: Sequence[GameParticle],
                              collision_handler: CollisionHandlerType = damaging_collision):
    bullets = sorted(bullets, key=lambda b: b.x - b.get_collision_rad())
    enemies = sorted(enemies, key=lambda b: b.x - b.get_collision_rad())
    # sep
    GROUP = [(0, 10), (10, 20), (20, float('inf'))]

    enemy_groups = [[p for p in enemies if left < p.get_collision_rad() <= right] for left, right in GROUP]
    bullet_groups = [[p for p in bullets if left < p.get_collision_rad() <= right] for left, right in GROUP]
    for enemy_group in enemy_groups:
        for bullet_group in bullet_groups:
            _collide_sorted_enemy_and_bullets(bullet_group, enemy_group, collision_handler)
