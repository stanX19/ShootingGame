from __future__ import annotations
import math
import random
from srcs.classes.entity.game_particle import GameParticle


def line_circle_first_intersect(line_start_x, line_start_y, line_end_x, line_end_y,
                                circle_center_x, circle_center_y, circle_radius):
    """
    Find the first intersection point between a line segment and a circle.

    Parameters:
        line_start_x (float): X-coordinate of the start of the line.
        line_start_y (float): Y-coordinate of the start of the line.
        line_end_x (float): X-coordinate of the end of the line.
        line_end_y (float): Y-coordinate of the end of the line.
        circle_center_x (float): X-coordinate of the circle's center.
        circle_center_y (float): Y-coordinate of the circle's center.
        circle_radius (float): Radius of the circle.

    Returns:
        tuple or None: The (x, y) coordinates of the first intersection point, or None if there is no intersection.
    """
    # Vector representation of the line
    dx = line_end_x - line_start_x
    dy = line_end_y - line_start_y

    # Vector from circle center to line start
    fx = line_start_x - circle_center_x
    fy = line_start_y - circle_center_y

    # Quadratic coefficients
    a = dx**2 + dy**2
    b = 2 * (fx * dx + fy * dy)
    c = fx**2 + fy**2 - circle_radius**2

    # Discriminant
    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        # No intersection
        return None

    # Find the two possible solutions (t-values for line equation)
    if a == 0:
        return None
    discriminant_sqrt = math.sqrt(discriminant)
    t1 = (-b - discriminant_sqrt) / (2 * a)
    t2 = (-b + discriminant_sqrt) / (2 * a)

    if t1 > t2:
        t1, t2 = t2, t1
    EPSILON = 1e-9  # Small tolerance for floating-point comparisons
    if -EPSILON <= t1 <= 1 + EPSILON:
        return line_start_x + t1 * dx, line_start_y + t1 * dy
    # second intersect is when line starts inside circle, reject
    # if -EPSILON <= t2 <= 1 + EPSILON:
    #     return line_start_x + t2 * dx, line_start_y + t2 * dy
    return None


def compute_circle_circle_overlap(x1, y1, r1, x2, y2, r2):
    d = math.hypot(x2 - x1, y2 - y1)
    if d >= r1 + r2:
        return 0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2

    r1_sq, r2_sq = r1**2, r2**2
    alpha1 = math.acos((d**2 + r1_sq - r2_sq) / (2 * d * r1))
    alpha2 = math.acos((d**2 + r2_sq - r1_sq) / (2 * d * r2))
    segment_area1 = r1_sq * alpha1 - 0.5 * r1_sq * math.sin(2 * alpha1)
    segment_area2 = r2_sq * alpha2 - 0.5 * r2_sq * math.sin(2 * alpha2)
    return segment_area1 + segment_area2


def circle_line_overlap(cx, cy, radius, x1, y1, x2, y2):
    import math

    # Line segment equation: (x, y) = (x1, y1) + t * ((x2 - x1), (y2 - y1))
    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy

    # Quadratic formula coefficients for intersection
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - radius * radius

    if a == 0:
        return 0
    # Discriminant
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return 0  # No intersection

    # Solve for t values (parametric intersection points)
    discriminant_sqrt = math.sqrt(discriminant)
    t1 = (-b - discriminant_sqrt) / (2 * a)
    t2 = (-b + discriminant_sqrt) / (2 * a)

    # Clamp t values to the range [0, 1] (segment endpoints)
    t1 = max(0, min(1, t1))
    t2 = max(0, min(1, t2))

    if t1 == t2:
        return 0  # No segment within the circle

    # Intersection points
    ix1, iy1 = x1 + t1 * dx, y1 + t1 * dy
    ix2, iy2 = x1 + t2 * dx, y1 + t2 * dy

    chord_length = math.hypot(ix2 - ix1, iy2 - iy1)
    return chord_length



def line_point_distance(sx1, sy1, sx2, sy2, px, py):
    if sx1 == sx2 and sy1 == sy2:
        return math.hypot(px - sx1, py - sy1)
    segment_length_squared = (sx2 - sx1) ** 2 + (sy2 - sy1) ** 2
    t = ((px - sx1) * (sx2 - sx1) + (py - sy1) * (sy2 - sy1)) / segment_length_squared
    t = max(0, min(1, t))
    closest_x = sx1 + t * (sx2 - sx1)
    closest_y = sy1 + t * (sy2 - sy1)
    return math.hypot(px - closest_x, py - closest_y)


def line_line_distance(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    distances = [
        line_point_distance(bx1, by1, bx2, by2, ax1, ay1),
        line_point_distance(bx1, by1, bx2, by2, ax2, ay2),
        line_point_distance(ax1, ay1, ax2, ay2, bx1, by1),
        line_point_distance(ax1, ay1, ax2, ay2, bx2, by2)
    ]
    return min(distances)


def can_catch_up(self: GameParticle, target: GameParticle):
    dx = target.x - self.x
    dy = target.y - self.y
    a = target.speed ** 2 - self.speed ** 2
    b = 2 * (dx * target.xv + dy * target.yv)
    c = dx ** 2 + dy ** 2
    disc = b ** 2 - 4 * a * c
    return disc >= 0


def calculate_intercept_angle(self: GameParticle, target: GameParticle):
    tx = target.x
    ty = target.y
    tvx = target.xv
    tvy = target.yv
    dx = tx - self.x
    dy = ty - self.y
    target_speed = math.hypot(tvx, tvy)
    a = target_speed ** 2 - self.speed ** 2
    b = 2 * (dx * tvx + dy * tvy)
    c = dx ** 2 + dy ** 2
    disc = b ** 2 - 4 * a * c

    if disc < 0:
        return math.atan2(dy, dx)
    try:
        t1 = (-b + math.sqrt(disc)) / (2 * a)
        t2 = (-b - math.sqrt(disc)) / (2 * a)
    except ZeroDivisionError:
        return math.atan2(dy, dx)
    t = min(t1, t2) if t1 > 0 and t2 > 0 else max(t1, t2, 0)
    intercept_x = tx + tvx * t
    intercept_y = ty + tvy * t
    return math.atan2(intercept_y - self.y, intercept_x - self.x)


def generate_random_point(rect_small: tuple[int, int, int, int], rect_big: tuple[int, int, int, int],
                          padding=0):
    small_x1, small_y1, small_x2, small_y2 = rect_small
    small_x1 -= padding
    small_x2 += padding
    small_y1 -= padding
    small_y2 += padding
    big_x1, big_y1, big_x2, big_y2 = rect_big

    # Check if rect_small completely contains rect_big
    if small_x1 <= big_x1 and small_y1 <= big_y1 and small_x2 >= big_x2 and small_y2 >= big_y2:
        raise ValueError("rect_small completely contains rect_big")

    # Ensure small rectangle is within the boundaries of the big rectangle
    small_x1 = max(small_x1, big_x1)
    small_y1 = max(small_y1, big_y1)
    small_x2 = min(small_x2, big_x2)
    small_y2 = min(small_y2, big_y2)

    # Calculate the areas outside the small rectangle but inside the big rectangle
    # 1. Left side of the small rectangle, contains top-left and bot-left corner
    left_area_width = max(small_x1 - big_x1, 0)
    left_area_height = big_y2 - big_y1
    left_area = left_area_width * left_area_height

    # 2. Right side of the small rectangle, contains top-right and bot-right corner
    right_area_width = max(big_x2 - small_x2, 0)
    right_area_height = big_y2 - big_y1
    right_area = right_area_width * right_area_height

    # 3. Top side of the small rectangle, do not contain corner
    top_area_width = small_x2 - small_x1
    top_area_height = max(big_y2 - small_y2, 0)
    top_area = top_area_width * top_area_height

    # 4. Bottom side of the small rectangle, do not contain corner
    bottom_area_width = small_x2 - small_x1
    bottom_area_height = max(small_y1 - big_y1, 0)
    bottom_area = bottom_area_width * bottom_area_height

    # Cumulative areas
    cumulative_areas = [left_area, left_area + right_area, left_area + right_area + top_area,
                        left_area + right_area + top_area + bottom_area]

    # Total valid area
    total_valid_area = cumulative_areas[-1]

    # Randomly select a region based on area proportion
    random_area = random.uniform(0, total_valid_area)

    # Binary search to find the selected region
    if random_area < cumulative_areas[0]:
        # In the left area
        x = random.uniform(big_x1, small_x1)
        y = random.uniform(big_y1, big_y2)
    elif random_area < cumulative_areas[1]:
        # In the right area
        x = random.uniform(small_x2, big_x2)
        y = random.uniform(big_y1, big_y2)
    elif random_area < cumulative_areas[2]:
        # In the top area
        x = random.uniform(small_x1, small_x2)
        y = random.uniform(small_y2, big_y2)
    else:
        # In the bottom area
        x = random.uniform(small_x1, small_x2)
        y = random.uniform(big_y1, small_y1)

    return (x, y)


def test(x, y, rad, rect, must_have: list[tuple[int, int, int, int]], must_error=False, iterations=10000):
    rect_small = [x - rad, y - rad, x + rad, y + rad]
    rect_big = rect

    points = []
    error_count = 0
    for _ in range(iterations):
        try:
            point = generate_random_point(rect_small, rect_big)
            points.append(point)
        except ValueError as e:
            error_count += 1

    def rect_contains(rect, cord) -> bool:
        x1, y1, x2, y2 = rect
        cord_x, cord_y = cord
        return x1 <= cord_x <= x2 and y1 <= cord_y <= y2

    if not all(any(rect_contains(rect, c) for c in points) for rect in must_have):
        return False
    if must_error and error_count == 0:
        return False
    return True


def main():
    case1 = [5, 5, 4, [0, 0, 10, 10], [[0, 0, 1, 1], [9, 9, 10, 10], [0, 9, 1, 10], [9, 0, 10, 1]]]

    print(test(*case1))

# def main():
#     import matplotlib.pyplot as plt
#     rect_big = [0, 0, 10, 10]
#
#     # Generate random points
#
#
#     # Unpack points
#     x_points, y_points = zip(*points)
#
#     # Plotting the rectangles and points
#     fig, ax = plt.subplots()
#     ax.set_aspect('equal')
#
#     # Plot rect_big
#     big_rect = plt.Rectangle((rect_big[0], rect_big[1]), rect_big[2] - rect_big[0], rect_big[3] - rect_big[1],
#                              fill=None, edgecolor='blue', linewidth=2)
#     ax.add_patch(big_rect)
#
#     # Plot rect_small
#     small_rect = plt.Rectangle((rect_small[0], rect_small[1]), rect_small[2] - rect_small[0],
#                                rect_small[3] - rect_small[1],
#                                fill=None, edgecolor='red', linewidth=2)
#     ax.add_patch(small_rect)
#
#     # Plot points
#     ax.scatter(x_points, y_points, color='green', s=1)
#
#     # Set limits and labels
#     ax.set_xlim(rect_big[0] - 1, rect_big[2] + 1)
#     ax.set_ylim(rect_big[1] - 1, rect_big[3] + 1)
#     ax.set_xlabel('X')
#     ax.set_ylabel('Y')
#     ax.set_title('Random Points Outside rect_small and Inside rect_big')
#
#     plt.show()


if __name__ == "__main__":
    main()

