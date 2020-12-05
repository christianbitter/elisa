from __future__ import annotations
from math import sqrt


class Vec:
    def __init__(self):
        super(Vec, self).__init__()
        self._v = []

    @property
    def dim(self):
        return len(self._v)

    def __len__(self):
        return self.dim

    @property
    def length(self):
        return sqrt(self.length_squared)

    def length_inv(self):
        return 1.0 / self.length

    @property
    def length_squared(self):
        s = [i * i for i in self._v]
        s_i = 0.0
        for i in s:
            s_i += i
        return s_i

    def length_squared_inv(self):
        return 1.0 / self.length_squared

    @property
    def is_zero(self):
        p0 = [x == 0.0 for x in self._v]
        return all(p0)

    def __getitem__(self, a):
        _a, _b = None, None
        if isinstance(a, int):
            _a, _b = a, a
            if a < 0 or a > 1:
                raise ValueError("a outside of bounds")
        if isinstance(a, slice):
            _a = a.start
            _b = a.stop
            if a.start > a.stop or a.stop > 1:
                raise ValueError("upper index outside of bounds or invalid")
        if _a == _b:
            return self._v[_a]
        else:
            return self._v[_a:_b]

    def __setitem__(self, a, b, c):
        _a, _b = None, None

        if isinstance(a, int):
            _a, _b = a, a
            if a < 0 or a > 1:
                raise ValueError("a outside of bounds")
        if isinstance(a, slice):
            _a, _b = a.start, a.stop
            if a.start > a.stop or a.stop > 1:
                raise ValueError("upper index outside of bounds or invalid")
        if _a == _b:
            self._v[_a] = c
        else:
            self._v[_a:_b] = c

    def __add__(self, other):
        raise ValueError("Not implemented")

    def __sub__(self, other):
        raise ValueError("Not implemented")

    def __mul__(self, other):
        raise ValueError("Not implemented")

    def __truediv__(self, other):
        raise ValueError("Not implemented")

    def dot(self, v):
        raise ValueError("Not implemented")

    def cross(self, v):
        raise ValueError("Not implemented")


def lerp1D(u, v, t: float) -> float:
    """
    lerp1D ( u, v, t ) = u + t * (v - u)
    :param u: any type that supports vector addition and scalar multiplication
    :param v: any type that supports vector addition and scalar multiplication
    :param t: (float) parameter at which interpolation is sought
    :return: (float) the interpolated value at the desired parameter
    """
    w = v - u
    return u + (w * t)


def angle(u: Vec, v: Vec) -> float:
    """
    Returns the cosine (angle) between two vectors u and v
    :param u: (Vec) vector u
    :param v: (Vec) vector v
    :return: The scaled dot product, cosine of u and v's angle
    """
    if u.is_zero or v.is_zero:
        raise ValueError("Angle with lower dimensional 0 vector cannot be determined")
    l_u = u.length
    l_v = v.length
    return u.dot(v) / (l_u * l_v)


def proj_u_v(u: Vec, v: Vec) -> Vec:
    """
    Returns the projection of vector u onto vector v
    :param u: (Vec) vector u
    :param v: (Vec) vector v
    :return: (Vec) the projection
    """
    if v.is_zero():
        raise ValueError("v cannot be the zero vector")
    uv = u.dot(v)
    k = v.length_squared_inv() * uv
    return k * v


def perp_u_v(u: Vec, v: Vec) -> Vec:
    """
    Returns the perpendicular component of vector u projected onto vector v
    :param u: (Vec) vector u
    :param v: (Vec) vector v
    :return: (Vec) the perpendicular component
    """
    p_u_v = proj_u_v(u, v)
    return u - p_u_v
