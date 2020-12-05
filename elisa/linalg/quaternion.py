from __future__ import annotations

from .linalg import is_numeric


class Quaternion(object):
    """Defines a Quaternion (see: https://de.wikipedia.org/wiki/Quaternion)
    https://www.youtube.com/watch?v=zjMuIxRvygQ
    """

    def __init__(self, x, y, z, w):
        super(Quaternion, self).__init__()
        self._x = x
        self._y = y
        self._z = z
        self._w = w

    def is_pure(self):
        return self._w == 0.0

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @property
    def w(self):
        return self._w

    def __add__(self, q: Quaternion):
        if not q:
            raise ValueError("q not provided")

        return Quaternion(self._x + q.x, self._y + q.y, self._z + q.z, self._w + q.w)

    def __sub__(self, q: Quaternion):
        if not q:
            raise ValueError("q not provided")

        return Quaternion(self._x - q.x, self._y - q.y, self._z - q.z, self._w - q.w)

    def __neg__(self):
        return Quaternion(-self._x, -self._y, -self._z, -self._w)

    def __mul__(self, q):
        if not q:
            raise ValueError("q not provided")

        if is_numeric(q):
            return Quaternion(self._x * q, self._y * q, self._z * q, self._w * q)
        elif isinstance(q, Quaternion):
            w = self._w * q.w - self._x * q.x - self._y * q.y - self._z * q.z
            x = self._w * q.x + self._x * q.w + self._y * q.z - self._z * q.y
            y = self._w * q.y - self._x * q.z + self._y * q.x + self._z * q.x
            z = self._w * q.z + self._x * q.y - self.y * q.x + self._z * q._w
            return Quaternion(x, y, z, w)
        else:
            raise ValueError("q not provided")

    def Re(self):
        return self._w

    def Im(self):
        return [self._x, self._y, self._z]

    def Dot(self, q: Quaternion) -> Quaternion:
        if not q:
            raise ValueError("q not provided")
        return Quaternion(self._x * q.x, self._y * q.y, self._z * q.z, self._w * q.w)

    def Cross(self, q: Quaternion) -> Quaternion:
        if not q:
            raise ValueError("q not provided")
        return Quaternion(
            self._y * q.z - self._z * q.y,
            self._z * q.x - self._x * q.z,
            self._x * q.y - self._y * q.x,
        )

    def __truediv__(self, q):
        if not q:
            raise ValueError("q not provided")

        if is_numeric(q):
            qinv = 1.0 / q
            return Quaternion(
                self._x * qinv, self._y * qinv, self._z * qinv, self._w * qinv
            )
        elif isinstance(q, Quaternion):
            iq = q.inverse()
            return self * iq
        else:
            raise ValueError("q not provided")

    def norm(self) -> float:
        return self._x ** 2 + self._y ** 2 + self._z ** 2 + self._w ** 2

    def is_norm(self) -> bool:
        return abs(self.norm()) == 1.0

    def conj(self):
        return Quaternion(-self._x, -self._y, -self._z, self._w)

    def inverse(self):
        ninv = 1.0 / self.norm()
        return self.conj() * ninv
