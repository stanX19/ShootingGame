import math

def normalize(value, min_val, max_val):
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    return min(max(value, min_val), max_val)

def angle_norm(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi

def angle_add(angle, add):
    return angle_norm(angle + add)

def angle_diff(dst, src):
    return angle_norm(dst - src)

def color_norm(color):
    return tuple(min(max(i, 0), 255) for i in color)

def color_intensity_shift(color: tuple, intensity: float):
    """

    :param color: (R, G, B)
    :param intensity: 0.0 ~ 1.0
    :return:
    """
    intensity = min(1.0, max(0.0, intensity))
    return color[0] * intensity, color[1] * intensity, color[2] * intensity