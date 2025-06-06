from __future__ import annotations
import pygame
import math

t_cord = tuple[float, float]

import pygame
import math


def draw_arrow(surface: pygame.Surface, start: tuple, end: tuple, color=(255, 255, 255), width=1):
    pygame.draw.line(surface, color, start, end, width)

    SIDE_LENGTH = 50
    ARROW_ANGLE = math.radians(30)
    theta = math.atan2(end[1] - start[1], end[0] - start[0])
    s1 = (end[0] - SIDE_LENGTH * math.cos(theta + ARROW_ANGLE),
          end[1] - SIDE_LENGTH * math.sin(theta + ARROW_ANGLE))
    s2 = (end[0] - SIDE_LENGTH * math.cos(theta - ARROW_ANGLE),
          end[1] - SIDE_LENGTH * math.sin(theta - ARROW_ANGLE))
    pygame.draw.line(surface, color, s1, end, width)
    pygame.draw.line(surface, color, s2, end, width)


def draw_cross(surface, x, y, rad, color1, color2):
    WIDTH = rad
    LENGTH = rad
    WIDTH -= WIDTH % 2   # ensure even
    LENGTH -= LENGTH % 2
    # pygame.draw.circle(surface, color1, (x, y), rad)
    pygame.draw.rect(surface, color1, (x - WIDTH // 2, y - LENGTH, WIDTH, 2 * LENGTH))
    pygame.draw.rect(surface, color1, (x - LENGTH, y - WIDTH // 2, 2 * LENGTH, WIDTH))


def draw_star(surface, x, y, rad, color1, color2):
    h1 = rad  # height of vertical and horizontal edge
    h2 = rad // 2  # height of diagonal edge
    w1 = h1 // 10  # width of vertical edge
    w2 = h2 // 4  # width of diagonal edge

    # comment follows cartesian
    draw_points = [
        (x, y + h1),  # Top
        (x + w1, y + w1 + w2),
        (x + h2, y + h2),
        (x + w1 + w2, y + w1),
        (x + h1, y),  # Right
        (x + w1 + w2, y - w1),
        (x + h2, y - h2),
        (x + w1, y - w1 - w2),
        (x, y - h1),  # Bot
        (x - w1, y - w1 - w2),
        (x - h2, y - h2),
        (x - w1 - w2, y - w1),
        (x - h1, y),  # Left
        (x - w1 - w2, y + w1),
        (x - h2, y + h2),
        (x - w1, y + w1 + w2),
    ]
    pygame.draw.circle(surface, color2, (x, y), radius=rad // 2)
    pygame.draw.polygon(surface, color1, draw_points)


def draw_up_arrow(surface, x, y, rad, color1, color2):
    w = rad
    h = rad
    pygame.draw.polygon(surface, color2, (
        (x, y - h),        # Top point
        (x - w, y),        # Bottom-left point
        (x - w // 2, y),        # Left inner point
        (x - w // 2, y + h), # Left inner bottom point
        (x + w // 2, y + h), # Right inner bottom point
        (x + w // 2, y),        # Right inner point
        (x + w, y)         # Bottom-right point
    ))
    w -= 3
    h -= 3
    pygame.draw.polygon(surface, color1, (
        (x, y - h),  # Top point
        (x - w, y),  # Bottom-left point
        (x - w // 2, y),  # Left inner point
        (x - w // 2, y + h),  # Left inner bottom point
        (x + w // 2, y + h),  # Right inner bottom point
        (x + w // 2, y),  # Right inner point
        (x + w, y)  # Bottom-right point
    ))
