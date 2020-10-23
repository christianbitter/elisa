# auth: christian bitter
# name: linalg.py
# desc: some math routines needed for our elisa things

# TODO: vec2d
# TODO: vec3d
# TODO: vec4d
# TODO: matrix2x2
# TODO: matrix3x3
# TODO: matrix4x4

from math import sqrt, pi

ALPHA_PI_INV = 1./ 180.
PI_INV       = 1./ pi
TWO_PI       = 2. * pi
H2_PI        = pi / 2.

def clampf(value:float, min_val:float=0., max_val:float=1.):
    return(min(max(value, min_val), max_val))

def is_numeric(v):
    return isinstance(v, float) or isinstance(v, int)

def angle_to_rad(alpha_angle:float):
    if not (0. <= alpha_angle <= 360.):
        raise ValueError("angle_to_rad - angle not in 0..360")
    if alpha_angle == 0.:
        return 0.
    elif alpha_angle == 90.:
        return H2_PI
    elif alpha_angle == 180.:
        return pi
    elif alpha_angle == 270.:
        return 1.5 * pi
    elif alpha_angle == 360.:
        return TWO_PI
    else:
        return pi * alpha_angle * ALPHA_PI_INV

    raise ValueError("not implemented")

def rad_to_angle(alpha_rad: float):
    if not 0. <= alpha_rad <= TWO_PI:
        raise ValueError(f"alpha_rad {alpha_rad} not in 0 .. 2PI")
    if alpha_rad == 0.:
        return 0.
    elif alpha_rad == TWO_PI:
        return 360.
    else:
        return alpha_rad * 180. * PI_INV