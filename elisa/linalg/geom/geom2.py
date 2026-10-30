from __future__ import annotations

from collections import namedtuple

from ..linalg import is_numeric
from ..ray2 import Ray2
from ..vec2 import Point2, Vec2

AABB = namedtuple("AABB", field_names=["xmin", "ymin", "xmax", "ymax"])

# TODO: general transformation matrix handling
# TODO: initial AABB in the constructors
# TODO: AABB change on change of x or y


class Poly2:
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
                    self._points.append(Point2(a=p[0], b=p[1]))
                else:
                    raise ValueError("p is not a point2 or tuple")

        _len = len(self._points)
        for _pidx in range(len(self._points)):
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

    @staticmethod
    def translate(poly, x: float, y: float) -> Poly2:
        if not poly:
            raise ValueError("poly not provided")

        if x == 0.0 and y == 0.0:
            return poly

        tv = Vec2(x, y)

        new_points = poly.points.copy()

        for i in range(len(new_points)):
            new_points[i] = new_points[i] + tv

        return Poly2(points=new_points)

    @property
    def edges(self) -> list:
        return self._edges

    def __add__(self, v) -> Poly2:
        if not v:
            raise ValueError("v not provided")

        _displace = Vec2(v)
        _p = self._points.copy()

        for i in range(len(_p)):
            _p[i] = _p[i] + _displace

        return Poly2(_p)

    def __sub__(self, v) -> Poly2:
        if not v:
            raise ValueError("v not provided")

        _displace = Vec2(v)
        _p = self._points.copy()

        for i in range(len(_p)):
            _p[i] = _p[i] - _displace

        return Poly2(_p)

    @property
    def AABB(self) -> AABB:
        # TODO: this can be optimized, move into construction, only changes when coordinate changes
        x = [p.x for p in self._points]
        y = [p.y for p in self._points]
        minx, miny = min(x), min(y)
        maxx, maxy = max(x), max(y)

        return AABB(minx, miny, maxx, maxy)


class Tri2(Poly2):
    """A 2-dimensional triangular shape"""

    def __init__(self, p0, p1, p2):
        """Create a new 2D triangle from three co-planar 2D points or two-dimensional numerical tuples.

        Args:
                        p0 (Point2 or 2D numerical tuple): first point
                        p1 (Point2 or 2D numerical tuple): second point
                        p2 (Point2 or 2D numerical tuple): third point
        """
        super().__init__([p0, p1, p2])
        self._p0 = (p0,)
        self._p1 = p1
        self._p2 = p2
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
    def intersect_ray(r: Ray2):
        raise ValueError("Not Implemented")

    def __iter__(self):
        return self._points.__iter__()

    def __getitem__(self, i: int) -> Point2:
        return self._points.__getitem__(i)

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

        minx, miny = min([self.x0.x, self.x1.x, self.x2.x]), min(
            [self.x0.y, self.x1.y, self.x2.y]
        )
        maxx, maxy = max([self.x0.x, self.x1.x, self.x2.x]), max(
            [self.x0.y, self.x1.y, self.x2.y]
        )

        self._aabb = AABB(minx, miny, maxx, maxy)

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
        return self._aabb

    @property
    def AABB(self) -> AABB:
        return self.bounding_rect()

    def __repr__(self) -> str:
        return f"Tri2: {self._p0}, {self._p1}, {self._p2}"

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Poly2)
            and len(o.points) == len(self.points)
            and all([self[i] == o[i] for i in range(len(self._points))])
        )