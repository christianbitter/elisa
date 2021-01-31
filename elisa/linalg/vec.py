from __future__ import annotations

import copy
from math import sqrt

from .linalg import is_numeric


class Vec:
    """A general n-dimensional vector class"""

    def __init__(self, v=None):
        super(Vec, self).__init__()
        if v is None:
            self._v = []
        else:
            if isinstance(v, Vec):
                self._v = v.v.copy()
            elif isinstance(v, list):
                self._v = v.copy()
            elif isinstance(v, tuple):
                self._v = list(v).copy()
            else:
                raise ValueError("v not a Vec, list or tuple type")

    def __copy__(self):
        return Vec(self.v)

    def __deepcopy__(self, memo):
        return Vec(copy.deepcopy(self.v, memo))

    def __repr__(self) -> str:
        return "Vec-{}: {}".format(self.dim, self._v.__repr__())

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def v(self):
        return self._v

    @property
    def dim(self):
        return len(self._v)

    def __len__(self):
        return self.dim

    @property
    def length(self):
        if len(self._v) == 0:
            return 0.0
        return sqrt(self.length_squared)

    def length_inv(self):
        if len(self._v) == 0:
            return 0.0
        return 1.0 / self.length

    @property
    def length_squared(self):
        if len(self._v) == 0.0:
            return 0.0

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
            if a < 0 or a >= len(self._v):
                raise ValueError("a outside of bounds")
        if isinstance(a, slice):
            _a = a.start
            _b = a.stop
            if a.start > a.stop or a.stop >= len(self._v):
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
        if other is None:
            raise ValueError("other vector not provided")
        if len(other) != len(self):
            raise AttributeError("vectors are of different dimensionality")

        if isinstance(other, Vec):
            return Vec([a + b for a, b in zip(self._v, other.v)])
        elif isinstance(other, tuple) or isinstance(other, list):
            return self.__add__(Vec(other))
        elif is_numeric(other):
            return self.__add__([other] * self.dim)
        else:
            raise ValueError("other not a Vec, list or tuple type")

    def __sub__(self, other):
        if other is None:
            raise ValueError("other vector not provided")
        if len(other) != len(self):
            raise AttributeError("vectors are of different dimensionality")

        if isinstance(other, Vec):
            return Vec([a - b for a, b in zip(self._v, other.v)])
        elif isinstance(other, tuple) or isinstance(other, list):
            return self.__sub__(Vec(other))
        elif is_numeric(other):
            return self.__sub__([other] * self.dim)
        else:
            raise ValueError("other not a Vec, list or tuple type")

    def __iter__(self):
        return self._v.__iter__()

    def __mul__(self, other):
        raise ValueError("Not implemented")

    def __truediv__(self, other):
        raise ValueError("Not implemented")

    def dot(self, v):
        raise ValueError("Not implemented")

    def cross(self, v):
        raise ValueError("Not implemented")


def mean(u: Vec) -> float:
    """Computes the mean of the vector u

    Args:
        u (Vec): vector of values

    Raises:
        ValueError: if u is not provided or u is of non-numeric integral type

    Returns:
        float: the mean
    """
    if not u:
        raise ValueError("u not provided")
    if u.dim < 1:
        return 0.0
    if is_numeric(u[0]) is False:
        raise ValueError("u is a vector of non-numeric integral type")

    m = len(u)
    minv = 1.0 / m
    return minv * sum(u.v)


def var(u: Vec) -> float:
    """Computes the variance of the vector components

    Args:
        u (Vec): vector of values

    Raises:
        ValueError: if u is not provided or u is of non-numeric integral type

    Returns:
        float: the variance of the vectors components
    """
    if not u:
        raise ValueError("u not provided")
    if u.dim < 2:
        return 0.0
    if is_numeric(u[0]) is False:
        raise ValueError("u is a vector of non-numeric integral type")

    m = len(u)
    minv = 1.0 / m
    mean_u = mean(u)
    return minv * sum([(x - mean_u) ** 2 for x in u])


def sd(u: Vec) -> float:
    """Computes the standard deviation of the vector components

    Args:
        u (Vec): vector of values

    Raises:
        ValueError: if u is not provided or u is of non-numeric integral type

    Returns:
        float: the sd of the vectors components
    """
    return sqrt(var(u))


def cov(u: Vec, v: Vec) -> float:
    """Computes the covariance between vectors u and v

    Args:
        u (Vec): vector of values
        v (Vec): vector of values

    Raises:
        ValueError: if u or v is not provided or u or v is of non-numeric integral type or u and v have different dimensions.

    Returns:
        float: the sd of the vectors components
    """
    if u is None or v is None:
        raise AttributeError("u or v not provided")
    if len(u) != len(v):
        raise AttributeError("u and v have different magnitude")
    if is_numeric(u[0]) is False or is_numeric(v[0]) is False:
        raise ValueError("u or v is a vector of non-numeric integral type")

    m = len(u)
    minv = 1.0 / m
    mean_u = mean(u)
    mean_v = mean(v)
    return minv * sum([(x - mean_u) * (y - mean_v) for x, y in zip(u, v)])


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
