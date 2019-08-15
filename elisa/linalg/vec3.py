from .linalg import is_numeric


class Vec3:

    def __init__(self, a, b, c):
        self._v = [float(a), float(b), float(c)]

    def __repr__(self):
        return "Vec3[{}, {}, {}]".format(self._v[0], self._v[1], self._v[2])

    @staticmethod
    def is_zero(v):
        return v[0] == 0. and v[1] == 0. and v[2] == 0.

    def __add__(self, other):
        return Vec3(self._v[0] + other[0], self._v[1] + other[1], self._v[2] + other[2])

    def __sub__(self, other):
        return Vec3(self._v[0] - other[0], self._v[1] - other[1], self._v[2] - other[2])

    @staticmethod
    def dot(u, v):
        return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]

    @staticmethod
    def mul(u, v):
        if isinstance(u, Vec3) and is_numeric(v):
            return Vec3(u[0] * v, u[1] * v, u[2] * v)
        if is_numeric(u) and isinstance(v, Vec3):
            return Vec3.mul(v, u)
        if isinstance(u, Vec3) and isinstance(v, Vec3):
            return Vec3(u[0] * v[0], u[1] * v[1], u[2] * v[2])
        raise ValueError("u and v must be numeric or Vec3 types")

    @staticmethod
    def div(u, v):
        if isinstance(u, Vec3) and is_numeric(v):
            vinv = 1. / v
            return Vec3(u[0] * vinv, u[1] * vinv, u[2 * vinv])
        if is_numeric(u) and isinstance(v, Vec3):
            return Vec3.div(v, u)
        if isinstance(u, Vec3) and isinstance(v, Vec3):
            return Vec3(u[0] / v[0], u[1] / v[1], u[2] / v[2])
        raise ValueError("u and v must be numeric or Vec3 types")

    def __mul__(self, other):
        return Vec3.mul(self, other)

    def __truediv__(self, other):
        return Vec3.div(self, other)

    @property
    def x(self):
        return self._v[0]

    @property
    def y(self):
        return self._v[1]

    @property
    def z(self):
        return self._v[2]

    def __getitem__(self, a):
        _a, _b = None, None
        if isinstance(a, int):
            _a, _b = a, a
            if a < 0 or a > 2:
                raise ValueError("a outside of bounds")
        if isinstance(a, slice):
            _a, _b = a.start, a.stop
            if a.start > a.stop or a.stop > 2:
                raise ValueError("upper index outside of bounds or invalid")
        if _a == _b:
            return self._v[_a]
        else:
            return self._v[_a:_b]

    @staticmethod
    def lerp(u, v, t: float):
        assert(isinstance(u, Vec3))
        assert(isinstance(v, Vec3))

        w = v - u
        return u + (w * t)

    def __setitem__(self, a, c):
        _a, _b = None, None
        if isinstance(a, int):
            _a, _b = a, a
            if a < 0 or a > 2:
                raise ValueError("a outside of bounds")
        if isinstance(a, slice):
            _a, _b = a.start, a.stop
            if a.start > a.stop or a.stop > 2:
                raise ValueError("upper index outside of bounds or invalid")
        if _a == _b:
            self._v[_a] = c
        else:
            self._v[_a:_b] = c


zero3 = Vec3(0, 0, 0)
one3 = Vec3(1, 1, 1)
