from __future__ import annotations

from ..ray2 import Ray2
from ..vec2 import Point2, Vec2
from .geom2 import AABB, Poly2


class Rect2(Poly2):
    """A 2-dimensional rectangular shape"""

    def __init__(self, p0, p1, p2, p3):
        """Create a new 2D rectangle from four co-planar 2D points or two-dimensional numerical tuples.

        Args:
            p0 (Point2 or 2D numerical tuple): first point
            p1 (Point2 or 2D numerical tuple): second point
            p2 (Point2 or 2D numerical tuple): second point
            p3 (Point2 or 2D numerical tuple): second point
        """
        # TODO: ensure proper order/ clockwise
        super().__init__([p0, p1, p2, p3])
        self._p0 = self._points[0]
        self._p1 = self._points[1]
        self._p2 = self._points[2]
        self._p3 = self._points[3]

        self._edge0 = self._edges[0]
        self._edge1 = self._edges[1]
        self._edge2 = self._edges[2]
        self._edge3 = self._edges[3]

        self._r0 = Ray2(p0, self._edge0)
        self._r1 = Ray2(p1, self._edge1)
        self._r2 = Ray2(p2, self._edge2)
        self._r3 = Ray2(p2, self._edge3)

        self._w = self._p2.x - self._p0.x
        self._h = self._p2.y - self._p0.y

        minx, miny = min([self.x0.x, self.x1.x, self.x2.x, self.x3.x]), min(
            [self.x0.y, self.x1.y, self.x2.y, self.x3.y]
        )
        maxx, maxy = max([self.x0.x, self.x1.x, self.x2.x, self.x3.x]), max(
            [self.x0.y, self.x1.y, self.x2.y, self.x3.y]
        )

        self._aabb = AABB(minx, miny, maxx, maxy)

    @property
    def width(self) -> float:
        """Returns the width of the rect

        Returns:
            float: width
        """
        return self._w

    @property
    def height(self) -> float:
        """Returns the height of the rect

        Returns:
            float: height
        """
        return self._h

    @property
    def edge0(self):
        return self._edge0

    @property
    def edge1(self):
        return self._edge1

    @property
    def edge2(self):
        return self._edge2

    @property
    def edge3(self):
        return self._edge3

    @staticmethod
    def intersect_ray(r: Ray2):
        # TODO:
        raise ValueError("Not Implemented")

    @property
    def bounding_rect(self) -> tuple:
        """Return the axis-aligned bounding rect as a four tuple (xmin, ymin, xmax, ymax)

        Returns:
            tuple: four tuple of the minimum and maximum coordinates respectively.
        """
        return self._aabb

    @property
    def AABB(self):
        return super().AABB

    def inside(self, p) -> bool:
        """Determines wether a single point (Point2 or x,y tuple) or a list of points is fully located inside this Rect2 instance.

        Args:
            p ([Point2, tuple (x,y) or list of the former]): point representation

        Raises:
            ValueError: if the point data is not provided

        Returns:
            bool: Returns True if the point or all points in case of collection is fully contained inside the Rect2 instance.
        """
        if not p:
            raise ValueError("p not provided")

        if isinstance(p, Poly2):
            return self.inside(p.points)
        if isinstance(p, list):
            point_list = p
            tests = [self.inside(_p) for _p in point_list]
            return all(tests)
        else:
            _p: Point2 = Point2(p)
            xmin, ymin, xmax, ymax = self.bounding_rect
            return _p.x >= xmin and _p.x <= xmax and _p.y >= ymin and _p.y <= ymax

    def __repr__(self) -> str:
        return f"Rect2: {self._p0}, {self._p1}, {self._p2}, {self._p3}"

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
    def x3(self) -> Point2:
        return self._points[3]

    def as_p_wh(self) -> tuple:
        """Returns the Rect2 in the format (x, y, w, h). This is suitable for pygame

        Returns:
            tuple: (x, y, w, h)
        """
        return (self.x0.x, self.x0.y, self.x2.x - self.x0.x, self.x2.y - self.x0.y)

    def __getitem__(self, i: int) -> Point2:
        return self._points.__getitem__(i)

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Rect2)
            and self[0] == o[0]
            and self[1] == o[1]
            and self[2] == o[2]
            and self[3] == o[3]
        )

    @staticmethod
    def create(p_min: Point2, p_max: Point2) -> Rect2:
        """Create a Rect2 from a min (left upper) and max (right lower) Point2 instance.

        Args:
            p_min (Point2): left-upper point
            p_max (Point2): right-lower point

        Returns:
            Rect2: The newly created rect
        """
        if not p_min:
            raise ValueError("Left upper point not supplied")
        if not p_max:
            raise ValueError("Right Lower point not supplied")

        p0, p1, p2, p3 = (
            p_min,
            Point2(p_max.x, p_min.y),
            p_max,
            Point2(p_min.x, p_max.y),
        )
        return Rect2(p0, p1, p2, p3)

    def __add__(self, v) -> Rect2:
        if not v:
            raise ValueError("v not provided")

        _displace = Vec2(v)

        _p0 = self.x0 + _displace
        _p1 = self.x1 + _displace
        _p2 = self.x2 + _displace
        _p3 = self.x3 + _displace

        return Rect2(_p0, _p1, _p2, _p3)

    def __sub__(self, v) -> Rect2:
        if not v:
            raise ValueError("v not provided")

        _displace = Vec2(v)

        _p0 = self.x0 - _displace
        _p1 = self.x1 - _displace
        _p2 = self.x2 - _displace
        _p3 = self.x3 - _displace

        return Rect2(_p0, _p1, _p2, _p3)

    def __str__(self):
        return f"R2(({self._p0[0]}, {self._p0[1]}), ({self._p1[0]}, {self._p1[1]}), ({self._p2[0]}, {self._p2[1]}), ({self._p3[0]}, {self._p3[1]}))"

    @staticmethod
    def from_coords(x_min: float, y_min: float, x_max: float, y_max: float) -> Rect2:
        """Create a rect2 instance from individual coordinates describing the
        extreme points of the rect.

        Args:
            x_min (float): minimum x coordinate
            y_min (float): minimum y coordinate
            x_max (float): maximum x coordinate
            y_max (float): maximum y coordinate

        Returns:
            Rect2: created Rect2 instance
        """
        if x_max < x_min:
            raise ValueError("xmax not >= xmin")
        if y_max < y_min:
            raise ValueError("ymax not >= ymin")

        return Rect2.create(Point2(x_min, y_min), Point2(x_max, y_max))

    @staticmethod
    def from_points(pmin: Point2, pmax: Point2) -> Rect2:
        """Create a rect2 instance from individual coordinates describing the
        extreme points of the rect.

        Args:
            pmin (Point2): minimum coordinate
            pmax (Point2): maximum coordinate

        Returns:
            Rect2: created Rect2 instance
        """
        return Rect2.from_coords(pmin.x, pmin.y, pmax.x, pmax.y)
