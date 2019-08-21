import math
from .linalg import is_numeric, Vec


class Vec2(Vec):

    def __init__(self, a, b):
        super(Vec2, self).__init__()
        self._v = [float(a), float(b)]

    def __repr__(self):
        return "Vec2[{}, {}]".format(self._v[0], self._v[1])

    def is_zero(self, v):
        return v[0] == 0. and v[1] == 0.

    def __add__(self, other):
        return Vec2(self._v[0] + other[0], self._v[1] + other[1])

    def __sub__(self, other):
        return Vec2(self._v[0] - other[0], self._v[1] - other[1])

    @staticmethod
    def dot(u, v):
        return u[0] * v[0] + u[1] * v[1]

    @staticmethod
    def mul(u, v):
        if isinstance(u, Vec2) and is_numeric(v):
            return Vec2(u[0] * v, u[1] * v)
        if is_numeric(u) and isinstance(v, Vec2):
            return Vec2.mul(v, u)
        if isinstance(u, Vec2) and isinstance(v, Vec2):
            return Vec2(u[0] * v[0], u[1] * v[1])
        raise ValueError("u and v must be numeric or Vec2 types")

    @staticmethod
    def div(u, v):
        if isinstance(u, Vec2) and is_numeric(v):
            return Vec2(u[0] / v, u[1] / v)
        if is_numeric(u) and isinstance(v, Vec2):
            return Vec2.div(v, u)
        if isinstance(u, Vec2) and isinstance(v, Vec2):
            return Vec2(u[0] / v[0], u[1] / v[1])
        raise ValueError("u and v must be numeric or Vec2 types")

    def dot(self, v):
        return Vec2.dot(self, v)

    def __mul__(self, other):
        return Vec2.mul(self, other)

    def __truediv__(self, other):
        return Vec2.div(self, other)

    @staticmethod
    def to_unit(v):
        assert(isinstance(v, Vec2))
        d = v.length
        d_inv = 1. / d
        return Vec2(v.x * d_inv, v.y * d_inv)

    @property
    def x(self):
        return self._v[0]

    @property
    def y(self):
        return self._v[1]


zero0 = Vec2(0, 0)
one2 = Vec2(1, 1)
