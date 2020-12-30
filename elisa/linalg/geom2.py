from __future__ import annotations

from .linalg import is_numeric
from .mat2 import Mat2
from .ray2 import Ray2
from .vec2 import Point2, Vec2

# TODO: general transformation matrix handling


class Poly2(object):
    """A 2-dimensional polygon object"""

    def __init__(self, points: list):
        """Create a 2-dimensional polygonal object from a list of 2-dimensional points.

        Args:
                        points (list): list of tuples of numerics or point2 instances from which the polygon is to be initialized

        Raises:
                        ValueError: if list does not contain tuple of numerics or tuple of point2 instances
        """
        super(Poly2, self).__init__()
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
    def AABB(self) -> tuple:
        # TODO: this can be optimized, but for now sufficient
        x = [p.x for p in self._points]
        y = [p.y for p in self._points]
        minx, miny = min(x), min(y)
        maxx, maxy = max(x), max(y)

        return (minx, miny, maxx, maxy)


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

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Circle2)
            and o.center_x == self.center
            and o.center_y == o.center
            and o.radius == self.radius
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

    @property
    def AABB(self) -> tuple:
        return self.bounding_rect()

    def __repr__(self) -> str:
        return "Tri2: {}, {}, {}".format(self._p0, self._p1, self._p2)

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Poly2)
            and len(o.points) == len(self.points)
            and all([self[i] == o[i] for i in range(len(self._points))])
        )


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
        super(Rect2, self).__init__([p0, p1, p2, p3])
        self._p0 = p0
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
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
    def intersect_ray(self, r: Ray2):
        # TODO:
        raise ValueError("Not Implemented")

    @property
    def bounding_rect(self) -> tuple:
        """Return the axis-aligned bounding rect as a four tuple (xmin, ymin, xmax, ymax)

        Returns:
            tuple: four tuple of the minimum and maximum coordinates respectively.
        """
        # TODO: this can be optimized, such that it is computed initially and
        # cashed until the points are transformed
        minx, miny = min([self.x0.x, self.x1.x, self.x2.x, self.x3.x]), min(
            [self.x0.y, self.x1.y, self.x2.y, self.x3.y]
        )
        maxx, maxy = max([self.x0.x, self.x1.x, self.x2.x, self.x3.x]), max(
            [self.x0.y, self.x1.y, self.x2.y, self.x3.y]
        )

        return minx, miny, maxx, maxy

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
        return "Rect2: {}, {}, {}, {}".format(self._p0, self._p1, self._p2, self._p3)

    def __str__(self) -> str:
        return self.__repr__()

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

    @staticmethod
    def from_points(x_min: float, y_min: float, x_max: float, y_max: float) -> Rect2:
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
