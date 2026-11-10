from ..geom import Circle2, Rect2, Tri2
from ..plane2 import Plane2
from ..ray2 import Ray2
from ..vec2 import Point2, Vec2


def intersection2(ray: Ray2, plane: Plane2):
    """Performs the intersection of a 2D ray with a 2D plane. If there is an intersection, the function returns a tuple indicating success
    the parameter t for which the intersection happened and the point of intersection.
    If the ray is perpendicular to the plane, then the result is False and None, None. If the ray points away from the plane, the result
    is False and the negative paramter t is provided, giving None for the point of intersection.

    Args:
                    ray (Ray2): Ray to intersect with the plane
                    plane (Plane2): Plane to intersect with the ray

    Returns:
                    [Triple]: Logical indicating if ray intersects plane, the paramter value for which the intersection happens (if any) and the point
                    on the plane where the intersection happens (if any).
    """
    # if the ray and plane normal are orthogonal no intersection
    d_n_rd = Vec2.dot(plane.normal, ray.direction)
    if d_n_rd == 0.0:
        return False, None, None
    # if the ray points into the opposite direction, no intersection with the plane but still a solution
    d_n_rp = Vec2.dot(plane.normal, ray.origin)
    t = (plane.w - d_n_rp) / d_n_rd
    intersects = t >= 0
    pos = None
    if intersects:
        pos = ray.origin + ray.direction * t
    return intersects, t, pos


def inside_rect2(rleftx: float, rlefty: float, w: float, h: float, p: Point2) -> bool:
    """Check if the point p is contained within the rect defined by left upper point (rleftx, rlefty) and
    tracing out the edges with width and height

    Args:
                    rleftx (float): x coordinate of left upper rectangle point
                    rlefty (float): y coordinate of left upper rectangle point
                    w (float): width of rect
                    h (float): height of rect
                    p (Point2): point to check for containment

    Returns:
                    bool: True if the point is contained inside of the rect
    """
    px = p.x
    py = p.y

    return (rleftx <= px <= rleftx + w) and (rlefty <= py <= rlefty + h)


def inside_square2(rleftx: float, rlefty: float, w: float, p: Point2) -> bool:
    return inside_rect2(rleftx, rlefty, w, w, p)


def inside_circle2(cx: float, cy: float, r: float, p: Point2) -> bool:
    """tests whether a point p is contained in a circle

    Args:
        cx (float): circle x
        cy (float): circle y
        r (float): radius of circle
        p (Point2): point to test

    Returns:
        bool: True if the point is contained in the circle, else False.
    """
    d = (Point2(cx, cy) - p).length
    return d <= r


def inside_triangle2(p0x, p0y, p1x, p1y, p2x, p2y, p: Point2) -> bool:
    """tests if some point p is inside the triangle defined by p0, p1, and p2.

    Args:
        p0x (_type_): x of p0
        p0y (_type_): y of p0
        p1x (_type_): x of p1
        p1y (_type_): y of p1
        p2x (_type_): x of p2
        p2y (_type_): y of p2
        p (Point2): the point to test for containment

    Returns:
        bool: True if p is in the triangle else False
    """
    return Tri2(Point2(p0x, p0y), Point2(p1x, p1y), Point2(p2x, p2y)).inside(p)


def intersects_AABB2(a: Rect2, b: Rect2) -> bool:
    """Determines if the two axis aligned bounding boxes a, and b intersect.

    Args:
        a (Rect2): first AAB
        b (Rect2): second AABB

    Returns:
        bool: if a and b intersect then True else False
    """
    if not a:
        raise ValueError("a not provided")
    if not b:
        raise ValueError("b not provided")

    a0x, a0y = a.x0.x, a.x0.y
    a2x, a2y = a.x2.x, a.x2.y

    b0x, b0y = b.x0.x, b.x0.y
    b2x, b2y = b.x2.x, b.x2.y

    # check that either of the boxes does not intersect
    return not (a0x > b2x or a2x < b0x or a0y > b2y or a2y < b0y)


def intersects_circle(a: Circle2, b: Circle2) -> bool:
    """tests whether the two circles a and b intersect

    Args:
        a (Circle2): circle 1
        b (Circle2): circle 2

    Returns:
        bool: true if the circles intersect otherwise false
    """
    rs = a.radius + b.radius
    ba = (b.center - a.center).length

    return ba <= rs


def area_of_intersection_AABB2(a: Rect2, b: Rect2) -> Rect2:
    """Computes the area of intersection from two axis aligned bounding boxes represented as two Rect2 instances.
    It is assumed that the two AABB intersect. No separate intersection test is performed.

    Args:
                    a (Rect2): first AABB
                    b (Rect2): second AABB

    Returns:
                    Rect2: the Area of intersection represented as a Rect2 instance
    """
    if not a:
        raise ValueError("a not provided")
    if not b:
        raise ValueError("b not provided")

    a0x, a0y = a.x0.x, a.x0.y
    a2x, a2y = a.x2.x, a.x2.y

    b0x, b0y = b.x0.x, b.x0.y
    b2x, b2y = b.x2.x, b.x2.y

    x0, x1 = max(a0x, b0x), min(a2x, b2x)
    y0, y1 = max(a0y, b0y), min(a2y, b2y)

    return Rect2.from_points(x0, y0, x1, y1)
