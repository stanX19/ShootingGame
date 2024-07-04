from __future__ import annotations
import math
import random
import pygame
import numpy as np
from srcs.classes.bullet_enemy_collider import collide_enemy_and_bullets
from srcs.classes.water_particle import WaterParticle
from srcs.classes import water_particle_collider
from srcs.constants import *


class WaterParticleHandler:
    def __init__(self, particles=None):
        if particles is None:
            particles = []
        self.particles: list[WaterParticle] = particles
        self.orbit_max_speed: float = 0.0
        self.orbit_acceleration: float = 0.0
        self.orbited_particle: [WaterParticle, None] = None

    def _draw_good_graphics(self, surface: pygame.Surface, focus: tuple[int, int]):
        draw_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        draw_surface.fill((0, 0, 0, 0))  # white background

        for particle in self.particles:
            particle_surface = pygame.Surface((particle.rad * 10, particle.rad * 10), pygame.SRCALPHA)
            particle_surface.fill((0, 0, 0, 0))
            color = (0, 255, 255, 25)
            pygame.draw.circle(particle_surface, color, (particle.rad, particle.rad), particle.rad)
            draw_surface.blit(
                particle_surface,
                (int(particle.x + focus[0] - particle.rad), int(particle.y + focus[1] - particle.rad))
            )
        # overlap = black
        alpha_array = pygame.surfarray.pixels_alpha(draw_surface)
        # if alpha is 0, alpha = 0, else alpha = ......
        alpha_array[:] = np.where(alpha_array == 0, 0, (355 - alpha_array) / 255 * 128)
        del alpha_array

        surface.blit(draw_surface, (-focus[0], -focus[1]))

    def draw_everything(self, surface: pygame.Surface, focus: tuple[int, int]):
        if GOOD_GRAPHICS:
            return self._draw_good_graphics(surface, focus)
        k = min(1, max(0, self.particles.__len__() / MAX_PARTICLE_COUNT - 1))
        color = (25 * (1 - k), 5 + 20 * k, 50 * k, 25)
        # color = (50 * k, 5 + 20 * (1 - k), 25 * (1 - k), 25)
        prev_rad = None
        particle_surface = None
        for particle in self.particles:
            if particle.rad != prev_rad:
                prev_rad = particle.rad
                particle_surface = pygame.Surface((particle.rad * 2, particle.rad * 2), pygame.SRCALPHA)
                particle_surface.fill((0, 0, 0, 0))
                pygame.draw.circle(particle_surface, color, (particle.rad, particle.rad), particle.rad)
            surface.blit(particle_surface, (particle.x - particle.rad, particle.y - particle.rad),
                         special_flags=pygame.BLEND_RGBA_ADD)
        # if self.orbited_particle:
        #     pygame.draw.circle(surface, (255, 255, 255),
        #                        (self.orbited_particle.x, self.orbited_particle.y), 10)

    def _collide_with_all_other(self, p1: WaterParticle, idx: int):
        for p2 in self.particles[idx + 1:]:
            if p2.x - p2.collide_rad > p1.x + p1.collide_rad:
                return
            distance = p1.distance_with(p2)
            water_particle_collider.adhesive_particle(p1, p2)
            if distance < p1.collide_rad + p2.collide_rad:
                water_particle_collider.collide_particle(p1, p2)
                water_particle_collider.repel_particle(p1, p2)

    def _collide_everything(self):
        self.particles.sort(key=lambda p: p.x - p.collide_rad)
        for idx, p1 in enumerate(self.particles):
            self._collide_with_all_other(p1, idx)

    def _spawn_at(self, x, y):
        random_angle = random.uniform(-math.pi, math.pi)
        self.particles.append(WaterParticle(x, y, random_angle, rad=15, lifespan=random.randint(10, 60)))

    def spawn_at(self, x, y):
        if len(self.particles) > MAX_PARTICLE_COUNT:
            return
        self._spawn_at(x, y)

    def _move(self):
        if self.orbited_particle and self.orbited_particle.lifespan < 0:
            self.orbited_particle = None
        if self.orbited_particle:
            power = self.orbited_particle.lifespan / 480
            radius = power * 300 + 200
            orbit_strength = 1
            self._attract_to(self.orbited_particle.x, self.orbited_particle.y,
                             radius, orbit_strength)
            ACCELERATION = 1.0
            if self.orbited_particle.speed < self.orbit_max_speed:
                self.orbited_particle.speed += ACCELERATION
            for p in self.particles:
                p.x += self.orbited_particle.xv
                p.y += self.orbited_particle.yv
            self.orbited_particle.move()
        for p in self.particles:
            p.move()

    def _attract_to(self, x, y, radius, factor):
        for p in self.particles:
            dy = y - p.y
            dx = x - p.x
            dis = math.hypot(dy, dx)
            if dis > radius or dis == 0:
                continue
            dy /= dis
            dx /= dis
            if self.orbited_particle and self.orbit_acceleration:
                p.speed += self.orbit_acceleration
            p.xv += dx * factor
            p.yv += dy * factor
            p.lifespan = random.randint(10, 30)

    def attract_to(self, x, y, radius=300, factor=1):
        self.orbited_particle = None
        self._attract_to(x, y, radius, factor)

    def collide_with_enemies(self, enemies):
        collide_enemy_and_bullets(self.particles, enemies)

    def remove_out_of_bounds(self, x_min, y_min, x_max, y_max):
        self.particles = list(filter(
            lambda p: x_min < p.x < x_max and y_min < p.y < y_max,
            self.particles
        ))

    def remove_zero_lifespan(self):
        self.particles = list(filter(
            lambda p: p.lifespan > 0,
            self.particles
        ))

    def remove_zero_hp(self):
        self.particles = list(filter(
            lambda p: p.hp > 0,
            self.particles
        ))

    def clear(self):
        self.particles = []

    def update(self):
        self._move()
        self._collide_everything()
        if not self.particles:
            self.orbited_particle = None

        if isinstance(self.orbited_particle, WaterParticle) and self.orbited_particle.speed == 0\
                and self.orbit_acceleration and self.particles.__len__() < MAX_PARTICLE_COUNT * 2:
            for _ in range(15):
                self._spawn_at(self.orbited_particle.x, self.orbited_particle.y)

    def release(self, mx, my, angle, speed, player):
        if not self.particles:
            return
        px = sum(p.x for p in self.particles) / len(self.particles)
        py = sum(p.y for p in self.particles) / len(self.particles)
        particle_mouse_dis = math.hypot(mx - px, my - py)
        mouse_player_dis = math.hypot(player.x - mx, player.y - my)
        pxv = sum(p.xv for p in self.particles) / len(self.particles) - player.xv
        pyv = sum(p.yv for p in self.particles) / len(self.particles) - player.yv
        particle_velocity = math.hypot(pxv, pyv)
        particle_speed = sum(p.speed for p in self.particles) / len(self.particles)
        directed_constant = particle_mouse_dis + particle_velocity * 10 - len(self.particles) / 100
        lifespan = 480
        self.orbit_max_speed = min(particle_mouse_dis * 0.1, max(p.speed for p in self.particles) * 2)
        # if particle_speed > 5:
        #     self.orbit_acceleration = particle_speed / 10
        # else:
        self.orbit_acceleration = 0.0
        if directed_constant > 50.0:
            particle_velocity = particle_mouse_dis * 0.005
            angle = math.atan2(my - py, mx - px)
        else:
            particle_velocity = 0
            self.orbit_max_speed = 0
            if particle_speed > 5:
                self.orbit_acceleration = particle_speed / 10
        self.orbited_particle = WaterParticle(px, py, angle, particle_velocity, lifespan=lifespan)


def main():
    particles = [
        WaterParticle(0, 0, 0, rad=30),  # --->
        WaterParticle(50, 0, math.pi, rad=30),  # <---
        WaterParticle(1000, 0, -math.pi / 2, rad=30),  # down
        WaterParticle(1000, 50, math.pi / 2, rad=30)  # up
    ]
    handler = WaterParticleHandler(particles)
    handler._collide_everything()

    for p in particles:
        print(f'Particle at ({p.x}, {p.y}) with velocity ({p.xv}, {p.yv})')


if __name__ == '__main__':
    main()
