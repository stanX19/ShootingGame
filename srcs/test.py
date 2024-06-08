import pygame
import numpy as np

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Particle:
    def __init__(self, x, y, rad):
        self.x = x
        self.y = y
        self.rad = rad

class ParticleSystem:
    def __init__(self):
        self.particles = [Particle(100, 100, 10), Particle(120, 120, 10)]  # Example particles

    def draw_everything(self, surface: pygame.Surface, focus: tuple[int, int]):
        draw_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        draw_surface.fill((0, 0, 0, 0))  # Transparent background

        for particle in self.particles:
            particle_surface = pygame.Surface((particle.rad * 10, particle.rad * 10), pygame.SRCALPHA)
            particle_surface.fill((0, 0, 0, 0))
            color = (0, 255, 255, 25)
            pygame.draw.circle(particle_surface, color, (particle.rad * 5, particle.rad * 5), particle.rad * 5)
            draw_surface.blit(
                particle_surface,
                (int(particle.x + focus[0] - particle.rad * 5), int(particle.y + focus[1] - particle.rad * 5))
            )

        # Convert Pygame surface to NumPy array
        draw_array = pygame.surfarray.array3d(draw_surface)
        alpha_array = pygame.surfarray.array_alpha(draw_surface)

        # Apply darkening effect
        darkened_array = np.maximum(0, draw_array - (alpha_array[..., None] // 2))

        # Create a new surface to hold the darkened image
        darkened_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Update the RGB values
        pygame.surfarray.blit_array(darkened_surface, darkened_array)

        # Update the alpha values
        darkened_alpha_array = pygame.surfarray.pixels_alpha(darkened_surface)
        darkened_alpha_array[:, :] = alpha_array // 2

        # Unlock the surfaces
        del draw_array
        del alpha_array
        del darkened_alpha_array

        # Blit the darkened surface onto the main surface
        surface.blit(darkened_surface, (0, 0))

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create particle system
particle_system = ParticleSystem()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    window.fill((255, 255, 255))  # Fill the background with white
    particle_system.draw_everything(window, (0, 0))  # Draw particles
    pygame.display.flip()

pygame.quit()
