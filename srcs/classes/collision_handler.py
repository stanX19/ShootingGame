from __future__ import annotations

import math
from typing import Callable, Any
import random

from srcs.classes import algo
from srcs.classes.entity.breakable import Breakable
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.entity.lazer import Lazer

CollisionHandlerType = Callable[[GameParticle, GameParticle], Any]

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


def damaging_collision(bullet: GameParticle, enemy: GameParticle):
    if bullet is enemy or bullet.is_dead() or bullet.hp <= 0 or enemy.is_dead() or enemy.hp <= 0:
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

def repel_collision(a: GameParticle, b: GameParticle):
    if (a is b) or a.is_dead() or a.hp <= 0 or b.is_dead() or b.hp <= 0:
        return
    elif isinstance(a, Lazer) or isinstance(b, Lazer):
        return

    if a.rad > b.rad:
        a, b = b, a
    dy = a.y - b.y
    dx = a.x - b.x
    dis = math.hypot(dy, dx)
    if dis == 0:
        dy = random.uniform(-0.1, 0.1)
        dx = random.uniform(-0.1, 0.1)
        dis = math.hypot(dy, dx)
    # a is smaller than b, a gets repelled
    overlap = a.rad + b.rad - dis
    a.x += dx / dis * overlap
    a.y += dy / dis * overlap