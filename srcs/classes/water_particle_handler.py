import math
import random
import pygame
from srcs.classes.bullet_enemy_collider import collide_enemy_and_bullets
from srcs.classes.water_particle import WaterParticle
from srcs.classes import water_particle_collider


class WaterParticleHandler:
    def __init__(self, particles=None):
        if particles is None:
            particles = []
        self.other_handlers: list[WaterParticleHandler] = []
        self.particles: list[WaterParticle] = particles
        self.orbit_max_speed: float = 0.0
        self.orbited_particle: [WaterParticle, None] = None

    def draw_everything(self, surface: pygame.Surface):
        # assert all radius is same
        prev_rad = None
        particle_surface = None
        for particle in self.particles:
            if particle.rad != prev_rad:
                prev_rad = particle.rad
                particle_surface = pygame.Surface((particle.rad * 2, particle.rad * 2), pygame.SRCALPHA)
                particle_surface.fill((0, 0, 0, 0))
                color = (0, 255, 255, 150)
                pygame.draw.circle(particle_surface, color, (particle.rad, particle.rad), particle.rad)
            if isinstance(particle_surface, pygame.Surface):
                surface.blit(particle_surface, (particle.x - particle.rad, particle.y - particle.rad),
                             special_flags=pygame.BLEND_RGBA_ADD)

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

    def spawn_at(self, x, y):
        random_angle = random.uniform(-math.pi, math.pi)
        self.particles.append(WaterParticle(x, y, random_angle, rad=15, lifespan=random.randint(10, 60)))

    def _move(self):
        if self.orbited_particle:
            power = self.orbited_particle.lifespan / 480
            self._attract_to(self.orbited_particle.x, self.orbited_particle.y,
                             power * 300, 0.7 * power + 1)
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
            p.xv += dx * factor
            p.yv += dy * factor
            p.lifespan = random.randint(5, 30)

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
        if self.orbited_particle:
            if self.orbited_particle.speed < self.orbit_max_speed:
                self.orbited_particle.speed *= 1.1
            self.orbited_particle.move()
            if self.orbited_particle.lifespan < 0:
                self.orbited_particle = None

    def release(self, x, y, angle, speed, player):
        particle_angle = sum(p.angle for p in self.particles) / len(self.particles)
        dx = x - sum(p.x for p in self.particles) / len(self.particles)
        dy = y - sum(p.y for p in self.particles) / len(self.particles)
        particle_dis = math.hypot(dx, dy)
        particle_xv = sum(p.xv for p in self.particles) / len(self.particles) - player.xv
        particle_yv = sum(p.yv for p in self.particles) / len(self.particles) - player.yv
        particle_speed = math.hypot(particle_xv, particle_yv)
        directed_constant = particle_dis + particle_speed * 10 - len(self.particles) / 100
        if directed_constant > 30.0:
            angle = math.atan2(dy, dx)
        else:
            particle_speed = 0.1
        self.orbit_max_speed = speed
        x -= dx * 0.7
        y -= dy * 0.7
        self.orbited_particle = WaterParticle(x, y, angle, particle_speed, lifespan=480)


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
