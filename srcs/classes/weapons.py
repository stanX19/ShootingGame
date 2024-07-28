import math
from srcs.constants import *


class WeaponType:
    def __init__(self, name: str, reload: float, velocity=BULLET_SPEED, count=None, radius=BULLET_RADIUS,
                 recoil=0, hp=1.0, dmg=1.0, spread=math.pi * 0.8, bullet_class="bullet",
                 min_bullet_count=1, growth_score=0.0, offset_factor=1.0, color=BULLET_COLOR):
        self.name: str = name
        self.shot_delay: float = reload
        self.speed: float = velocity
        if count is None:
            count = int(reload * 0.01) + 1
        self.bullet_count: int = count
        self.rad: float = radius
        self.recoil: float = recoil
        self.hp: float = hp
        self.dmg: float = dmg
        self.spread: float = spread
        self.min_bullet_count: int = min_bullet_count
        self.growth_factor: float = growth_score
        self.offset_factor: float = offset_factor
        self.bullet_class: str = bullet_class
        self.color: tuple[int] = color

    def __str__(self):
        return self.name

    pass


class WeaponEnum:
    machine_gun = WeaponType("machine gun", reload=100, velocity=10, count=10, radius=2, growth_score=25000,
                             offset_factor=0.1)
    lazer = WeaponType("lazer", reload=200, velocity=100, count=100, radius=1)
    shotgun = WeaponType("shotgun", reload=1000, velocity=50, count=100, radius=1,
                         recoil=PLAYER_SPEED, dmg=1, min_bullet_count=10, growth_score=2500)
    bomb = WeaponType("bomb", reload=800, velocity=5, count=1, radius=25, recoil=25, hp=10000, dmg=10)
    missile = WeaponType("missile", 500, count=8, growth_score=50000, dmg=10,
                         radius=MISSILE_RADIUS, velocity=MISSILE_SPEED)
    shield = WeaponType("shield", reload=30000, velocity=1, count=200, hp=500, radius=1,
                        dmg=1 / ENEMY_RADIUS * ENEMY_SPEED, spread=2*math.pi,
                        min_bullet_count=30, growth_score=2500)
    nova = WeaponType("nova", reload=0, count=min(1, int(MAX_PARTICLE_COUNT / 100)), velocity=1000)
