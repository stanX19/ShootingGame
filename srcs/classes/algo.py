import math
import random
from srcs.classes.game_particle import GameParticle


def calculate_intercept_angle(self: GameParticle, target: GameParticle):
    tx = target.x
    ty = target.y
    tvx = target.xv
    tvy = target.yv
    dx = tx - self.x
    dy = ty - self.y
    target_speed = math.hypot(tvx, tvy)
    a = target_speed ** 2 - (self.speed * 0.1) ** 2
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

#
# def main():
#     import matplotlib.pyplot as plt
#     rect_small = [2, 2, 8, 8]
#     rect_big = [0, 0, 10, 10]
#
#     # Generate random points
#     points = []
#     for _ in range(1000):
#         try:
#             point = generate_random_point(rect_small, rect_big, padding=1)
#             points.append(point)
#         except ValueError as e:
#             print(e)
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
#
#
# if __name__ == "__main__":
#     main()
#
