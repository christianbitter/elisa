from __future__ import annotations

from .linalg import is_numeric
from .vec2 import Point2, Vec2
from .ray2 import Ray2


class Poly2(object):
    """A 2-dimensional polygon object"""

    def __init__(self, points: list):
        """Create a 2-dimensional polygonal object from a list of 2-dimensional points.

        Args:
                        points (list): list of tuples of numerics or point2 instances from which the polygon is to be initialized

        Raises:
                        ValueError: if list does not contain tuple of numerics or tuple of point2 instances
        """
        super().__init__()
        self._points = []
        self._edges = []
        if points and len(points) > 0:
            for p in points:
                if isinstance(p, Point2):
                    self._points.append(p)
                elif isinstance(p, tuple) and len(p) == 2 and is_numeric(p):
                    self._points.append(Point2(p))
                else:
                    raise ValueError("p is not a point2 or tuple")

        _len = len(self._points)
        for _pidx in range(len(self._points) - 1):
            _next_p_idx = (_pidx + 1) % _len
            pi = self._points[_pidx]
            pj = self._points[_next_p_idx]
            self._edges.append(pj - pi)

    def __iter__(self):
        return self._points.__iter__()

    def __len__(self):
        return self._points.__len__()

    @property
    def points(self) -> list:
        return self._points

    @property
    def edges(self) -> list:
        return self._edges


# Circle is not a Poly per se, but nonetheless
class Circle2(Poly2):
    def __init__(self, p, radius: float):
        super(Circle2, self).__init__(points=[p])
        self._radius = radius

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
        return "Circle({}^2 + {}^2 = {}^2)".format(
            self._points[0].x, self._points[0].y, self._radius
        )


class Tri2(Poly2):
    """A 2-dimensional triangular shape"""

    def __init__(self, p0, p1, p2):
        """Create a new 2D triangle from three co-planar 2D points or two-dimensional numerical tuples.

        Args:
                        p0 (Point2 or 2D numerical tuple): first point
                        p1 (Point2 or 2D numerical tuple): second point
                        p2 (Point2 or 2D numerical tuple): third point
        """
        super(Tri2, self).__init__([p0, p1, p2])
        self._edge0 = p1 - p0
        self._edge1 = p2 - p1
        self._edge2 = p0 - p2
        self._r0 = Ray2(p0, self._edge0)
        self._r1 = Ray2(p1, self._edge1)
        self._r2 = Ray2(p2, self._edge2)

    @property
    def edge0(self):
        return self._edge0

    @property
    def edge1(self):
        return self._edge1

    @property
    def edge2(self):
        return self._edge2

    @staticmethod
    def intersect_ray(self, r: Ray2):
        raise ValueError("Not Implemented")

    def inside(self, p: Point2) -> bool:
        """Determines if the point p lies inside or on the edge of the triangle by performing a half-space test of the point against the individual triangle edges.

        Args:
                        p (Point2): point to test

        Returns:
                        bool: True if the point lies inside the triangle or on the it's edges, else False.
        """
        hs0 = self._r0.half_space(p)
        hs1 = self._r1.half_space(p)
        hs2 = self._r2.half_space(p)

        return hs0 <= 0 and hs1 <= 0 and hs2 <= 0

    @property
    def x0(self) -> Point2:
        return self._points[0]

    @property
    def x1(self) -> Point2:
        return self._points[1]

    @property
    def x2(self) -> Point2:
        return self._points[2]

    @property
    def e0(self) -> Vec2:
        return self._points[1] - self._points[0]

    @property
    def e1(self) -> Vec2:
        return self._points[2] - self._points[1]

    @property
    def e2(self) -> Vec2:
        return self._points[0] - self._points[2]

    def bounding_rect(self) -> tuple:
        minx, miny = min([self.x0.x, self.x1.x, self.x2.x]), min(
            [self.x0.y, self.x1.y, self.x2.y]
        )
        maxx, maxy = max([self.x0.x, self.x1.x, self.x2.x]), max(
            [self.x0.y, self.x1.y, self.x2.y]
        )

        return (minx, miny, maxx, maxy)
