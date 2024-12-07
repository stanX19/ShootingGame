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
    :return: (R, G, B) with adjusted intensity
    """
    intensity = min(1.0, max(0.0, intensity))
    return tuple(int(c * intensity) for c in color)


def color_mix(color1, color2, weight1=1.0, weight2=1.0):
    """
    :param color1: (R, G, B)
    :param color2: (R, G, B)
    :param weight1: float
    :param weight2: float
    :return: (R, G, B)
    """
    # Normalize weights
    total_weight = weight1 + weight2
    weight1 /= total_weight
    weight2 /= total_weight

    # Mix colors
    mixed_color = (
        int(color1[0] * weight1 + color2[0] * weight2),
        int(color1[1] * weight1 + color2[1] * weight2),
        int(color1[2] * weight1 + color2[2] * weight2)
    )

    # Normalize the mixed color
    return color_norm(mixed_color)
