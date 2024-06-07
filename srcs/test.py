import pygame
import random

class Particle:
    def __init__(self, x, y, xv, yv, mass, rad):
        self.x = x
        self.y = y
        self.xv = xv
        self.yv = yv
        self.mass = mass
        self.rad = rad


class Simulation:
    def __init__(self):
        self.particles = []

    def add_particle(self, particle):
        self.particles.append(particle)

    def draw_everything(self, surface: pygame.Surface):
        draw_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        draw_surface.fill((0, 0, 0, 0))  # white background

        for particle in self.particles:
            color = (0, 255, 255, 25)
            pygame.draw.circle(draw_surface, color, (particle.x, particle.y), particle.rad * 5)

        surface.blit(draw_surface, (0, 0))



# Example usage
pygame.init()
screen = pygame.display.set_mode((800, 600))

simulation = Simulation()
for _ in range(100):  # Adding multiple particles
    x = random.randint(100, 700)
    y = random.randint(100, 500)
    simulation.add_particle(Particle(x, y, 0, 0, 1, 6))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((90, 90, 0))  # Clear screen with black background
    simulation.draw_everything(screen)
    pygame.display.flip()

pygame.quit()
