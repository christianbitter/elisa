from pytest import raises

from elisa.linalg import Point2
from elisa.linalg.geom import Circle2
from elisa.linalg.intersection import intersects_circle


def test_circle():
    assert Circle2(Point2(0.0, 0.0), 1.0)


def test_no_circle():
    with raises(ValueError):
        Circle2(Point2(0.0, 0.0), 0.0)


def test_intersect_circles():
    c1 = Circle2(Point2(0.0, 0.0), 1.0)
    c2 = Circle2(Point2(2.0, 0.0), 1.0)
    c3 = Circle2(Point2(3.0, 0.0), 1.0)

    assert intersects_circle(c1, c2)
    assert not intersects_circle(c1, c3)
    assert intersects_circle(c2, c3)
