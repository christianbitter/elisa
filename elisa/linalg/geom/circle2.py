from __future__ import annotations

import random

from ..vec2 import Point2
from .geom2 import AABB, Poly2


class Circle2(Poly2):
    def __init__(self, p: Point2, radius: float):
        """Create a 2D circle at some point p with a defined radius

        Args:
            p (Point2): center of circle
            radius (float): radius of the circle
        """
        super().__init__(points=[p])

        if radius <= 0:
            raise ValueError("radius must be positive")

        self._radius = radius
        cx, cy, r = self.center_x, self.center_y, radius
        self._aabb = AABB(cx - r, cy - r, cx + r, cy + r)

    def set_xy(self, x: float, y: float) -> Circle2:
        r = self.radius
        self._points[0] = Point2(x, y)
        self._aabb = AABB(x - r, y - r, x + r, y + r)

    @property
    def a(self):
        return -2.0 * self.center_x

    @property
    def b(self):
        return -2.0 * self.center_y

    @property
    def c(self):
        return self.radius**2 - self.center_x**2 - self.center_y**2

    def expanded_form(self) -> str:
        return f"x^2 + y^2 + {self.a}x + {self.b}y = {self.c}"

    @property
    def center(self) -> Point2:
        return self._points[0]

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def center_x(self) -> float:
        return self._points[0].x

    @property
    def center_y(self) -> float:
        return self._points[0].y

    def __repr__(self):
        return (
            f"Circle({self._points[0].x}^2 + {self._points[0].y}^2 = {self._radius}^2)"
        )

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Circle2)
            and o.center == self.center
            and o.radius == self.radius
        )

    @property
    def AABB(self) -> AABB:
        return self._aabb

    @staticmethod
    def random(max_x: float, max_y: float, max_r: float) -> Circle2:
        if max_r <= 0.0:
            raise ValueError("radius cannot be <= 0")
        cx = random.random()
        cy = random.random()
        cr = random.random()

        return Circle2(Point2(cx * max_x, cy * max_y), cr * max_r)
