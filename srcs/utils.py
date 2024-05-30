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