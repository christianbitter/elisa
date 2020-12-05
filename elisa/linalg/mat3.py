from __future__ import annotations

import math
from .linalg import is_numeric
from .vec3 import Point3, Vec3

# TODO: is orthogonal
# TODO: is orthonormal
# TODO: cross product


class Mat3:
    """
    A 3x3 matrix, built in row-wise order. That is the values a, b, c, d, e, f, g, h, i
    go into:
    a | b | c
    ---------
    d | e | f
    ---------
    g | h | i
    """

    def __init__(self, a, b, c, d, e, f, g, h, i):
        self._v = [a, b, c, d, e, f, g, h, i]

    @property
    def shape(self):
        return 3, 3

    def __getitem__(self, i):
        if 0 <= i <= 8:
            return self._v[i]
        else:
            raise ValueError("index wrong")

    def __setitem__(self, i, v):
        if v is None:
            raise ValueError("v not provided")

        if 0 <= i <= 8:
            self._v[i] = v
        else:
            raise ValueError("index for assignment is outside of [0, 8]")

    def __add__(self, other):
        if is_numeric(other):
            return self.__add__(
                Mat3(other, other, other, other, other, other, other, other, other)
            )
        elif isinstance(other, Mat3):
            return Mat3(
                self._v[0] + other[0],
                self._v[1] + other[1],
                self._v[2] + other[2],
                self._v[3] + other[3],
                self._v[4] + other[4],
                self._v[5] + other[5],
                self._v[6] + other[6],
                self._v[7] + other[7],
                self._v[8] + other[8],
            )
        else:
            raise ValueError("other has incompatible type")

    def __sub__(self, other):
        if is_numeric(other):
            return self.__sub__(
                Mat3(other, other, other, other, other, other, other, other, other)
            )
        elif isinstance(other, Mat3):
            return Mat3(
                self._v[0] - other[0],
                self._v[1] - other[1],
                self._v[2] - other[2],
                self._v[3] - other[3],
                self._v[4] - other[4],
                self._v[5] - other[5],
                self._v[6] - other[6],
                self._v[7] - other[7],
                self._v[8] - other[8],
            )
        else:
            raise ValueError("other has incompatible type")

    def __mul__(self, other):
        if is_numeric(other):
            return Mat3(
                self._v[0] * other,
                self._v[1] * other,
                self._v[2] * other,
                self._v[3] * other,
                self._v[4] * other,
                self._v[5] * other,
                self._v[6] * other,
                self._v[7] * other,
                self._v[8] * other,
            )
        elif isinstance(other, Vec3):
            return Vec3(
                self._v[0] * other[0] + self._v[1] * other[1] + self._v[2] * other[2],
                self._v[3] * other[0] + self._v[4] * other[1] + self._v[5] * other[2],
                self._v[6] * other[0] + self._v[7] * other[1] + self._v[8] * other[2],
            )
        elif isinstance(other, Mat3):
            v0, o0 = self._v[0], other[0]
            v1, o1 = self._v[1], other[1]
            v2, o2 = self._v[2], other[2]
            v3, o3 = self._v[3], other[3]
            v4, o4 = self._v[4], other[4]
            v5, o5 = self._v[5], other[5]
            v6, o6 = self._v[6], other[6]
            v7, o7 = self._v[7], other[7]
            v8, o8 = self._v[8], other[8]
            return Mat3(
                v0 * o0 + v1 * o3 + v2 * o6,
                v0 * o1 + v1 * o4 + v2 * o7,
                v0 * o2 + v1 * o5 + v2 * o8,
                v3 * o0 + v4 * o3 + v5 * o6,
                v3 * o1 + v4 * o4 + v5 * o7,
                v3 * o2 + v4 * o5 + v5 * o8,
                v6 * o0 + v7 * o3 + v8 * o6,
                v6 * o1 + v7 * o4 + v8 * o7,
                v6 * o2 + v7 * o5 + v8 * o8,
            )
        else:
            raise ValueError(
                "Matrix multiplication for the provided type combination not implemented"
            )

    def __truediv__(self, other):
        if is_numeric(other):
            other_inv = 1.0 / other
            return self * other_inv
        elif isinstance(other, Mat3):
            return self * Mat3.inverse(other)
        else:
            raise ValueError("Divide does not support the type: {}".format(type(other)))

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
    def e(self):
        return self._v[4]

    @property
    def f(self):
        return self._v[5]

    @property
    def g(self):
        return self._v[6]

    @property
    def h(self):
        return self._v[7]

    @property
    def i(self):
        return self._v[8]

    @property
    def trace(self) -> float:
        """Computes the trace of the matrix, i.e. the sum of diagonal elements.

        Returns:
                        float: the trace.
        """
        return self._v[0] + self._v[4] + self._v[8]

    @property
    def diag(self) -> list:
        """Returns the set of diagonal elements of the matrix

        Returns:
                        list: list of three floats given by the matrix diagonal
        """
        return [self._v[0], self._v[4], self._v[8]]

    @property
    def det(self):
        return Mat3.determinant(self)

    @property
    def inv(self):
        return Mat3.inverse(self)

    @staticmethod
    def inverse(m: Mat3) -> Mat3:
        """Computes the inverse of the provided matrix

        Args:
                        m (Mat3): the matrix for which we desire to compute the inverse.

        Raises:
                        ValueError: if the matrix is none, or the matrix's determinant is 0

        Returns:
                        Mat3: the inverse to the provided matrix
        """
        if not m:
            raise ValueError("Matrix not provided")

        d = m.det
        if d == 0.0:
            raise ValueError("Matrix cannot be inverted, determinant is 0")

        d_inv = 1.0 / d

        a11, a12, a13 = m.a, m.b, m.c
        a21, a22, a23 = m.d, m.e, m.f
        a31, a32, a33 = m.g, m.h, m.i

        i11 = d_inv * (a22 * a33 - a23 * a32)
        i12 = d_inv * (a13 * a32 - a12 * a33)
        i13 = d_inv * (a12 * a23 - a13 * a22)
        i21 = d_inv * (a23 * a31 - a21 * a33)
        i22 = d_inv * (a11 * a33 - a13 * a31)
        i23 = d_inv * (a13 * a21 - a11 * a23)
        i31 = d_inv * (a21 * a32 - a22 * a31)
        i32 = d_inv * (a12 * a31 - a11 * a32)
        i33 = d_inv * (a11 * a22 - a12 * a21)

        return Mat3(i11, i12, i13, i21, i22, i23, i31, i32, i33)

    @staticmethod
    def determinant(m: Mat3) -> float:
        """Computes the determinant of the matrix

        Args:
                        m (Mat3): the matrix to compute the determinant for

        Raises:
                        ValueError: if matrix is none

        Returns:
                        float: the determinant
        """
        if not m:
            raise ValueError("Matrix cannot be none")

        a11, a12, a13 = m.a, m.b, m.c
        a21, a22, a23 = m.d, m.e, m.f
        a31, a32, a33 = m.g, m.h, m.i

        d = (
            a11 * (a22 * a33 - a23 * a32)
            - a12 * (a21 * a33 - a23 * a31)
            + a13 * (a21 * a32 - a22 * a31)
        )
        return d

    @staticmethod
    def transpose(m):
        return m.t

    @property
    def c0(self):
        return [self._v[0], self._v[3], self._v[5]]

    @property
    def c1(self):
        return [self._v[1], self._v[4], self._v[7]]

    @property
    def c2(self):
        return [self._v[2], self._v[5], self._v[8]]

    @property
    def r0(self):
        return [self._v[0], self._v[1], self._v[2]]

    @property
    def r1(self):
        return [self._v[3], self._v[4], self._v[5]]

    @property
    def r2(self):
        return [self._v[6], self._v[7], self._v[8]]

    @property
    def t(self):
        return Mat3(
            self._v[0],
            self._v[3],
            self._v[6],
            self._v[1],
            self._v[4],
            self._v[7],
            self._v[2],
            self._v[5],
            self._v[8],
        )

    def __str__(self):
        return """[Mat3]
                [{}, {}, {}
                    {}, {}, {}
                    {}, {}, {}]""".format(
            *self._v
        )


zero3 = Mat3(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
one3 = Mat3(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
eye3 = Mat3(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)


def translate2D(x: float, y: float) -> Mat3:
    m = Mat3(1.0, 0.0, x, 0.0, 1.0, y, 0.0, 0.0, 1.0)
    return m
