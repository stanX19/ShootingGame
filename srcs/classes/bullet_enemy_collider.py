from __future__ import annotations
import math
from typing import Sequence
from srcs.constants import *
from srcs.classes.game_particle import GameParticle
from srcs.classes.enemy import Enemy


def handle_collision(bullet: GameParticle, enemy: GameParticle):
    if bullet.is_dead() or bullet.hp <= 0:
        return
    if enemy.is_dead() or enemy.hp <= 0:
        return
    enemy.hp -= bullet.dmg
    bullet.hp -= enemy.dmg
    # if enemy.hp > 0 and isinstance(enemy, Enemy):
    #     enemy.find_new_target()
    # if bullet.hp > 0 and isinstance(bullet, Enemy):
    #     bullet.find_new_target()


def check_collision_with_enemies(bullet: GameParticle, enemies: list[GameParticle], start_idx: int):
    for enemy in enemies[start_idx:]:
        if enemy.x + enemy.rad < bullet.x - bullet.rad:
            start_idx += 1
            continue
        break
    for enemy in enemies[start_idx:]:
        if enemy.x - enemy.rad > bullet.x + bullet.rad:
            break
        if math.hypot(enemy.x - bullet.x, enemy.y - bullet.y) < enemy.rad + bullet.rad:
            handle_collision(bullet, enemy)
    return start_idx


def _collide_sorted_enemy_and_bullets(bullets: list[GameParticle], enemies: list[GameParticle]):
    enemy_start_idx = 0
    for bullet in bullets:
        enemy_start_idx = check_collision_with_enemies(bullet, enemies, enemy_start_idx)
        if enemy_start_idx >= len(enemies):
            break


def collide_enemy_and_bullets(bullets: Sequence[GameParticle], enemies: Sequence[GameParticle]):
    bullets = sorted(bullets, key=lambda b: b.x - b.rad)
    enemies = sorted(enemies, key=lambda b: b.x - b.rad)
    # sep
    CUTTING_LINE = ENEMY_RADIUS + 20

    small_enemies = [p for p in enemies if p.rad <= CUTTING_LINE]
    big_enemies = [p for p in enemies if p.rad > CUTTING_LINE]
    _collide_sorted_enemy_and_bullets(bullets, small_enemies)
    _collide_sorted_enemy_and_bullets(bullets, big_enemies)
