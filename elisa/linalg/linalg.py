# auth: christian bitter
# name: linalg.py
# desc: some math routines needed for our elisa things

from math import sqrt, pi

ALPHA_PI_INV = 1.0 / 180.0
PI_INV = 1.0 / pi
TWO_PI = 2.0 * pi
H2_PI = pi / 2.0


def clampf(value: float, min_val: float = 0.0, max_val: float = 1.0):
    return min(max(value, min_val), max_val)


def is_numeric(v) -> bool:
    """Returns true if is a numeric type (int or float) or contains numeric elements if this is a tuple

    Args:
        v ([type]): can be tuple or a primitive type

    Returns:
        bool: true if v is numeric or in case of a tuple, all of v's members are numeric
    """
    if isinstance(v, tuple):
        return all([is_numeric(_x) for _x in v])
    else:
        return isinstance(v, float) or isinstance(v, int)


def angle_to_rad(alpha_angle: float):
    if not (0.0 <= alpha_angle <= 360.0):
        raise ValueError("angle_to_rad - angle not in 0..360")
    if alpha_angle == 0.0:
        return 0.0
    elif alpha_angle == 90.0:
        return H2_PI
    elif alpha_angle == 180.0:
        return pi
    elif alpha_angle == 270.0:
        return 1.5 * pi
    elif alpha_angle == 360.0:
        return TWO_PI
    else:
        return pi * alpha_angle * ALPHA_PI_INV

    raise ValueError("not implemented")


def rad_to_angle(alpha_rad: float):
    if not 0.0 <= alpha_rad <= TWO_PI:
        raise ValueError(f"alpha_rad {alpha_rad} not in 0 .. 2PI")
    if alpha_rad == 0.0:
        return 0.0
    elif alpha_rad == TWO_PI:
        return 360.0
    else:
        return alpha_rad * 180.0 * PI_INV
