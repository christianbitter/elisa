import pytest
from pytest import raises

from elisa.linalg import Point2, Vec2
from elisa.linalg.geom import Circle2
from elisa.linalg.intersection import intersects_circle
from elisa.physix.collision import circle_circle

import logging


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def test_circle():
    assert Circle2(Point2(0.0, 0.0), 1.0)


def test_no_circle():
    with raises(ValueError):
        Circle2(Point2(0.0, 0.0), 0.0)


# test circle of equal radius touch in one point
# test circle of equal radius touch in two points
# test circle of equal radius do not touch
# test circle of different radius touch in one point - one inside the other
# test circle of different radius touch in two points - one inside the other
# test circle of different radius do not touch - one inside the other


def test_intersect_circles():
    c1 = Circle2(Point2(0.0, 0.0), 1.0)
    c2 = Circle2(Point2(2.0, 0.0), 1.0)
    c3 = Circle2(Point2(3.0, 0.0), 1.0)

    assert intersects_circle(c1, c2)
    assert not intersects_circle(c1, c3)
    assert intersects_circle(c2, c3)


def test_coefficients():
    c1 = Circle2(Point2(1.0, 1.0), 1.0)

    assert c1.a == -2.0
    assert c1.b == -2.0
    assert c1.c == -1.0


def test_intersect_c2c_none():
    c1 = Circle2(Point2(1.0, 0.0), 1.0)
    c2 = Circle2(Point2(1.5, 0.0), 0.25)
    c3 = Circle2(Point2(1.0, 0.0), 4.0)
    c4 = Circle2(Point2(1.0, 3.0), 1.0)
    # no contact
    assert circle_circle(c1, c2) is None
    assert circle_circle(c1, c4) is None
    assert circle_circle(c1, c3) is None


def test_intersect_c2c_one():
    c1 = Circle2(Point2(1.0, 0.0), 1.0)
    c2 = Circle2(Point2(3.0, 0.0), 1.0)
    c3 = Circle2(Point2(1.0, 2.0), 1.0)

    c4 = Circle2(Point2(100.0, 100.0), 50.0)
    c5 = Circle2(Point2(200.0, 100.0), 50.0)

    manif = circle_circle(c1, c1)

    assert manif
    assert manif.depth == 2.0
    assert manif.normal == Vec2([0.0, 1.0])
    assert len(manif.contact) == 1

    manif = circle_circle(c1, c2)

    # single contact
    assert manif
    assert manif.depth == 0.0
    assert manif.normal == (c2.center - c1.center).to_unit()
    assert len(manif.contact) == 1 and manif.contact[0] == Point2(1.0, 0.0)

    manif = circle_circle(c1, c3)

    # single contact
    assert manif
    assert manif.depth == 0.0
    assert manif.normal == (c3.center - c1.center).to_unit()
    assert len(manif.contact) == 1 and manif.contact[0] == Point2(0.0, 1.0)

    manif = circle_circle(c4, c5)

    # single contact
    assert manif
    assert manif.depth == 0.0
    assert manif.normal == (c5.center - c4.center).to_unit()
    assert len(manif.contact) == 1

    print(manif.contact)


def test_intersect_c2c_two():
    c1 = Circle2(Point2(0.0, 0.0), 1.0)
    c2 = Circle2(Point2(1.5, 0.0), 1.0)

    c3 = Circle2(Point2(450.0, 400.0), 75.0)
    c4 = Circle2(Point2(525.0, 350.0), 30.0)

    manif = circle_circle(c1, c2)

    # single contact
    assert manif
    assert manif.depth == 0.0
    assert len(manif.contact) == 2

    manif = circle_circle(c3, c4)

    # single contact
    assert manif
    assert manif.depth == 0.0
    assert len(manif.contact) == 2
