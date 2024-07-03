import math
from srcs.constants import *


class WeaponType:
    def __init__(self, name, reload, velocity=BULLET_SPEED, count=None, radius=BULLET_RADIUS,
                 recoil=0, hp=1.0, dmg=1.0, spread=math.pi * 0.8, bullet_class="bullet",
                 min_bullet_count=1, growth_factor=0.0, offset_factor=1.0):
        self.name = name
        self.shot_delay = reload
        self.speed = velocity
        if count is None:
            count = int(reload * 0.01) + 1
        self.bullet_count = count
        self.rad = radius
        self.recoil = recoil
        self.hp = hp
        self.dmg = dmg
        self.spread = spread
        self.min_bullet_count = min_bullet_count
        self.growth_factor = growth_factor
        self.offset_factor = offset_factor
        self.bullet_class = bullet_class

    def __str__(self):
        return self.name

    pass


class WeaponEnum:
    machine_gun = WeaponType("machine gun", reload=100, velocity=10, count=10, radius=2, growth_factor=50000,
                             offset_factor=0.1)
    lazer = WeaponType("lazer", reload=200, velocity=100, count=100, radius=1)
    shotgun = WeaponType("shotgun", reload=1000, velocity=50, count=100, radius=1,
                         recoil=PLAYER_SPEED, dmg=1, min_bullet_count=10, growth_factor=5000)
    bomb = WeaponType("bomb", reload=800, velocity=5, count=1, radius=25, recoil=25, hp=10000, dmg=10)
    missile = WeaponType("missile", 500, count=8, growth_factor=100000, dmg=10,
                         radius=MISSILE_RADIUS, velocity=MISSILE_SPEED)
    shield = WeaponType("shield", reload=30000, velocity=1, count=200, hp=500, radius=1,
                        dmg=1 / ENEMY_RADIUS * ENEMY_SPEED, spread=2*math.pi,
                        min_bullet_count=30, growth_factor=5000)
    nova = WeaponType("nova", reload=0, count=min(1, int(MAX_PARTICLE_COUNT / 100)), velocity=1000)
