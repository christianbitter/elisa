import math
from .linalg import is_numeric

# TODO: general functions ... is orthogonal, is orthonormal

class Mat2:
    """
    A 2x2 matrix, built in row-wise order. That is the values a, b, c, d
    go into:
    a | b
    -----
    c | d
    """
    def __init__(self, a, b, c, d):
        self._v = [a, b, c, d]

    @property
    def shape(self):
        return 2, 2

    def __getitem__(self, i):
        if 0 <= i <= 3:
            return self._v[i]
        else:
            raise ValueError("index wrong")

    def __add__(self, other):
        if is_numeric(other):
            return self.__add__(Mat2(other, other, other, other))
        else:
            return Mat2(self._v[0] + other[0],
                        self._v[1] + other[1],
                        self._v[2] + other[2],
                        self._v[3] + other[3])

    def __sub__(self, other):
        if is_numeric(other):
            return self.__add__(Mat2(other, other, other, other))
        else:
            return Mat2(self._v[0] - other[0],
                        self._v[1] - other[1],
                        self._v[2] - other[2],
                        self._v[3] - other[3])

    def __mul__(self, other):
        if is_numeric(other):
            return Mat2(self._v[0] * other, self._v[1] * other, self._v[2] * other, self._v[3] * other)
        else:
            raise ValueError("Not implemented")

    def __truediv__(self, other):
        if is_numeric(other):
            other_inv = 1. / other
            return Mat2(self._v[0] * other_inv, self._v[1] * other_inv, self._v[2] * other_inv, self._v[3] * other_inv)
        else:
            return self * Mat2.inverse(other)

    @property
    def a(self):
        return self._v[0]

    @property
    def b(self):
        return self._v[1]

    @property
    def c(self):
        return self._v[2]

    @property
    def d(self):
        return self._v[3]

    @property
    def trace(self):
        return self._v[0] + self._v[3]

    @property
    def diag(self):
        return [self._v[0], self._v[3]]

    @property
    def det(self):
        return Mat2.determinant(self)

    @property
    def inv(self):
        return Mat2.inverse(self)

    @staticmethod
    def inverse(m):
        assert(isinstance(m, Mat2))
        d = m.det
        if d == 0.:
            raise ValueError("Matrix cannot be inverted, determinant is 0")
        d_inv = 1. / d
        return Mat2(d_inv * m.d, d_inv * -1. * m.b, d_inv * -1. * m.c, d_inv * m.a)

    @staticmethod
    def determinant(m):
        assert(isinstance(m, Mat2))
        return m[0] * m[3] - m[1] * m[2]

    @staticmethod
    def transpose(m):
        return m.t

    @property
    def c0(self):
        return [self._v[0], self._v[2]]

    @property
    def c1(self):
        return [self._v[1], self._v[3]]

    @property
    def r0(self):
        return [self._v[0], self._v[1]]

    @property
    def r1(self):
        return [self._v[2], self._v[3]]

    @property
    def t(self):
        return Mat2(self._v[0], self._v[2], self._v[1], self._v[3])

    def __str__(self):
        return """[Mat2]
                [{}, {}
                 {}, {}]""".format(self._v[0], self._v[1], self._v[2], self._v[3])


zero2 = Mat2(0., 0., 0., 0.)
one2  = Mat2(1., 1., 1., 1.)
eye2  = Mat2(1., 0., 0., 1.)