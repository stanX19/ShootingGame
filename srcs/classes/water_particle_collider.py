import math
import random
from srcs.classes.water_particle import WaterParticle


def repel_particle(p1: WaterParticle, p2: WaterParticle):
    # Vector from p1 to p2
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    distance = math.hypot(dy, dx)

    if distance == 0:
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        distance = math.hypot(dy, dx)
    # Calculate the overlap distance
    overlap = p1.collide_rad + p2.collide_rad - distance

    if overlap > 0:
        # Normal vector (unit vector)
        nx = dx / distance
        ny = dy / distance

        # Displace each particle along the normal vector by half the overlap distance
        p1.x -= nx * overlap / 2
        p1.y -= ny * overlap / 2
        p2.x += nx * overlap / 2
        p2.y += ny * overlap / 2


def adhesive_particle(p1: WaterParticle, p2: WaterParticle, adhesive_strength=0.01, adhesion_distance=10):
    # Calculate the difference in position
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    # Calculate the distance between the particles
    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    nx = dx / distance
    ny = dy / distance

    adhesion_distance += p1.collide_rad + p2.collide_rad
    if distance < adhesion_distance:
        # Calculate the adhesive force magnitude
        force_magnitude = adhesive_strength * (adhesion_distance - distance)

        # Apply adhesive force to both particles
        p1_force_x = force_magnitude * nx / p1.mass
        p1_force_y = force_magnitude * ny / p1.mass
        p2_force_x = -force_magnitude * nx / p2.mass
        p2_force_y = -force_magnitude * ny / p2.mass

        p1.xv += p1_force_x
        p1.yv += p1_force_y
        p2.xv += p2_force_x
        p2.yv += p2_force_y


def collide_particle(p1: WaterParticle, p2: WaterParticle):
    # Calculate the difference in position and velocity
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dvx = p2.xv - p1.xv
    dvy = p2.yv - p1.yv

    # Calculate the distance between the particles
    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance == 0:
        return

    # Calculate the normal vector (normalized)
    nx = dx / distance
    ny = dy / distance

    # Calculate the relative velocity in terms of the normal direction
    dv_dot_n = dvx * nx + dvy * ny

    # Calculate the mass ratio
    m1 = p1.mass
    m2 = p2.mass

    # Calculate the new velocities along the normal direction
    if dv_dot_n > 0:  # They are moving away from each other, no need to collide
        return

    # Conservation of momentum and energy along the normal direction
    # Formulae derived from the 1D elastic collision equations
    new_v1n = (p1.xv * nx + p1.yv * ny * (m1 - m2) + 2 * m2 * (p2.xv * nx + p2.yv * ny)) / (m1 + m2)
    new_v2n = (p2.xv * nx + p2.yv * ny * (m2 - m1) + 2 * m1 * (p1.xv * nx + p1.yv * ny)) / (m1 + m2)

    # Update velocities in the normal direction
    p1.xv += (new_v1n - (p1.xv * nx + p1.yv * ny)) * nx
    p1.yv += (new_v1n - (p1.xv * nx + p1.yv * ny)) * ny
    p2.xv += (new_v2n - (p2.xv * nx + p2.yv * ny)) * nx
    p2.yv += (new_v2n - (p2.xv * nx + p2.yv * ny)) * ny
