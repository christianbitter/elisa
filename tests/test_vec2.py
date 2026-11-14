import pytest

from elisa.linalg import Vec2


def test_vec2():
    v0 = Vec2(0.0, 0.0)
    assert v0 == Vec2.ZERO()
    assert v0.is_zero()


def test_vec2_add():
    assert Vec2.ZERO() + Vec2.ZERO() == Vec2.ZERO()


def test_vec2_sub():
    v1 = Vec2(1.0, 0.0)
    assert Vec2.ZERO() - Vec2.ZERO() == Vec2.ZERO()
    assert v1 - Vec2.ZERO() == v1
    assert v1 - v1 == Vec2.ZERO()


def test_vec2_rotate():
    assert Vec2.rotate(Vec2.ZERO(), 0) == Vec2.ZERO()

    r1 = Vec2.rotate(Vec2(1.0, 0.0), 90.0)
    assert r1.x == pytest.approx(0.0) and r1.y == pytest.approx(1.0)

    r2 = Vec2.rotate(Vec2(0.0, 1.0), -90.0)

    assert r2.x == pytest.approx(1.0) and r2.y == pytest.approx(0.0)

def test_vec2_angle():
    assert Vec2(1., 0.).to_angle(True) == 0.
    assert Vec2(0., 1.).to_angle(True) == 90.
    assert Vec2(-1., 0.).to_angle(True) == 180.
    assert Vec2(1., 1.).to_angle(True) == 45.


def test_proj():
    v0 = Vec2(1.0, 1.0)
    v1 = Vec2(1.0, 0.0)

    assert v0.project_onto(v1) == Vec2(1.0, 0.0)
