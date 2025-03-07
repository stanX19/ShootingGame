from __future__ import annotations

import math
from typing import Callable

from srcs.classes import algo
from srcs.classes.entity.breakable import Breakable
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.entity.lazer import Lazer
from collections import defaultdict
from typing import Sequence


def lazer_unit_collision(l: Lazer, p: GameParticle):
    # print(f"before: {l.hp:.2f} {p.hp:.2f}")
    intersect = algo.line_circle_first_intersect(l.x, l.y, l.end_x, l.end_y, p.x, p.y, p.rad)
    if intersect is None:
        intersect = [l.x, l.y]
        distance = 0
    else:
        distance = math.hypot(intersect[0] - l.x, intersect[1] - l.y)
    # dmg factor enough to kill either (or both survives)
    dmg_factor = abs(l.hp - (distance / l.rad))
    dmg_factor = min(dmg_factor, p.hp / max(0.1 ,l.dmg))

    l.hp -= min(1.0, p.dmg) * dmg_factor
    p.hp -= l.dmg * dmg_factor
    l.update_length()
    # print(f"after: ({intersect[0]:.2f}, {intersect[1]:.2f}) {distance=:.2f} {dmg_factor=:.2f}, {l.hp:.2f} {p.hp:.2f}")

CollisionHandlerType = Callable[[GameParticle, GameParticle], None]

def handle_collision(bullet: GameParticle, enemy: GameParticle):
    if bullet.is_dead() or bullet.hp <= 0 or enemy.is_dead() or enemy.hp <= 0:
        return
    elif isinstance(bullet, Lazer) and not isinstance(enemy, Lazer):
        lazer_unit_collision(bullet, enemy)
    elif isinstance(enemy, Lazer) and not isinstance(bullet, Lazer):
        lazer_unit_collision(enemy, bullet)
    else:
        enemy.hp -= bullet.dmg
        bullet.hp -= enemy.dmg

    if enemy.is_dead():
        bullet.add_score(enemy.base_score)
    if bullet.is_dead():
        enemy.add_score(enemy.base_score)
    if isinstance(enemy, Breakable):
        enemy.handle_hit_by(bullet)
    if isinstance(bullet, Breakable):
        bullet.handle_hit_by(enemy)


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
                    handle_collision(bullet, enemy)

def check_collision_with_enemies(bullet: GameParticle, enemies: list[GameParticle], start_idx: int,
                              collision_handler:CollisionHandlerType = handle_collision):
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
                              collision_handler:CollisionHandlerType = handle_collision):
    enemy_start_idx = 0
    for bullet in bullets:
        enemy_start_idx = check_collision_with_enemies(bullet, enemies, enemy_start_idx, collision_handler)
        if enemy_start_idx >= len(enemies):
            break


def collide_enemy_and_bullets(bullets: Sequence[GameParticle], enemies: Sequence[GameParticle],
                              collision_handler: CollisionHandlerType = handle_collision):
    bullets = sorted(bullets, key=lambda b: b.x - b.get_collision_rad())
    enemies = sorted(enemies, key=lambda b: b.x - b.get_collision_rad())
    # sep
    GROUP = [(0, 10), (10, 20), (20, float('inf'))]

    enemy_groups = [[p for p in enemies if left <= p.get_collision_rad() <= right] for left, right in GROUP]
    bullet_groups = [[p for p in bullets if left <= p.get_collision_rad() <= right] for left, right in GROUP]
    for enemy_group in enemy_groups:
        for bullet_group in bullet_groups:
            _collide_sorted_enemy_and_bullets(bullet_group, enemy_group, collision_handler)
