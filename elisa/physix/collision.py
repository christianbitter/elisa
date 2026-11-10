import logging
import math

from ..linalg import Vec2, Point2, Mat2
from ..linalg.geom import AABB, Circle2
from .manifold import Manifold

logger = logging.getLogger(__name__)

# TODO: construct the full manifold

# - coincident circles: normal ``(0, 1)``, depth ``r_a + r_b``, contact
#   ``a.center + normal * r_a``. The contact set is the whole circumference, so
#   this is one documented representative on A's boundary, not "all points";


def circle_circle(c1: Circle2, c2: Circle2) -> Manifold | None:
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

    depth = 0.0
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
    # and circle_aabb for walls by clamping the centre into the box.
    raise ValueError("TODO: circle-aabb")
