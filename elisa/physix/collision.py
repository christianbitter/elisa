import logging
import math

from ..linalg import Point2, Vec2
from ..linalg.geom import AABB, Circle2
from .manifold import Manifold

logger = logging.getLogger(__name__)


def circle_circle(c1: Circle2, c2: Circle2) -> Manifold | None:
    """computes the intersection between two circles. Two circles and can intersect in 0, 1, or two points.
    Here, we treat the case of circles that are identical as a special case, with just one intersection.

    Args:
        c1 (Circle2): first circle
        c2 (Circle2): second circle

    Raises:
        ValueError: if the circles are not provided

    Returns:
        Manifold | None: if the circles intersect, a manifold is returned.
    """
    r12 = c1.radius + c2.radius

    if c1 == c2:
        n = Vec2(0.0, 1.0)
        return Manifold(depth=r12, normal=n, contact=[c1.center + n * c1.radius])

    d = c2.center - c1.center
    d0 = d.to_unit()
    d12 = d.length

    # add one circle contained in the other - d is smaller then the sum of rs but ...
    if any([d12 > r12, d12 + c2.radius < c1.radius, d12 + c1.radius < c2.radius]):
        return None

    depth = c1.radius + c2.radius - d
    contacts = []

    if math.isclose(d12, r12):
        # one intersection point
        logger.info("Circles collide in single point")
        p = d0 * c1.radius
        contacts = [p]
    else:
        logger.info("Circles collide in two points")
        # translate so that c1 is at origin
        dc1 = c1.center
        c1new = Circle2(Point2(0.0, 0.0), c1.radius)
        c2new = Circle2(c2.center - dc1, c2.radius)

        alpha = c2new.center.to_angle(True)

        if not math.isclose(alpha, 0.0):
            # let's rotate - c2new, because c1new forms the basis of the coordinate system
            cc2new = Vec2.rotate(c2new.center, -alpha)
            c2new = Circle2(cc2new, c2new.radius)

        a, b, c = c1new.a, c1new.b, c1new.c
        d, e, f = c2new.a, c2new.b, c2new.c

        dinv = 1.0 / d

        x = dinv * (f - c)

        y1 = math.sqrt(c - x**2)
        y2 = -y1

        v1 = Vec2(x, y1)
        v2 = Vec2(x, y2)

        if not math.isclose(alpha, 0.0):
            # now rotate back
            v1 = Vec2.rotate(v1, alpha)
            v2 = Vec2.rotate(v2, alpha)

        # now translate back
        v1 += dc1
        v2 += dc1
        contacts = [v1, v2]

    return Manifold(normal=d0, depth=depth, contact=contacts)


def circle_aabb(c: Circle2, aabb: AABB) -> Manifold | None:
    """computes the intersection of a circle with an aabb.
    The circle may intersect with 0, 1, or 2 points on each of the manifolds half-planes/ lines.

    Args:
        c (Circle2): the circle
        aabb (AABB): the aabb

    Raises:
        ValueError: if either object is not provided

    Returns:
        Manifold | None: in case there is an intersection a manifold is returned.
    """
    # and circle_aabb for walls by clamping the centre into the box.
    raise ValueError("TODO: circle-aabb")
