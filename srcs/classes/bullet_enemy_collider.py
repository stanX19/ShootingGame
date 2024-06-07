import math
from srcs.classes.bullet import Bullet
from srcs.classes.enemy import Enemy


def handle_collision(bullet: Bullet, enemy: Enemy):
    if bullet.hp <= 0:
        return
    enemy.hp -= bullet.dmg
    bullet.hp -= bullet.dmg + enemy.hp


def check_collision_with_enemies(bullet: Bullet, enemies: list[Enemy], start_idx: int):
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


def collide_enemy_and_bullets(bullets, enemies):
    bullets.sort(key=lambda b: b.x - b.rad)
    enemies.sort(key=lambda b: b.x - b.rad)

    enemy_start_idx = 0
    for bullet in bullets:
        enemy_start_idx = check_collision_with_enemies(bullet, enemies, enemy_start_idx)
        if enemy_start_idx >= len(enemies):
            break
