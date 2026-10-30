from __future__ import annotations

from ..vec2 import Point2
from .geom2 import AABB, Poly2


class Circle2(Poly2):
    def __init__(self, p:Point2, radius: float):
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

    def set_x(self, x):
        dx = x - self._points[0].x
        self._points[0].x = x

        self._aabb.xmin += dx
        self._aabb.xmax += dx

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

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Circle2)
            and o.center_x == self.center
            and o.center_y == o.center
            and o.radius == self.radius
        )

    @property
    def AABB(self) -> AABB:
        return self._aabb
