import pytest

from elisa.linalg import Vec2


def test_vec2():
    v0 = Vec2(0.0, 0.0)
    assert v0 == Vec2.ZERO()
    assert v0.is_zero()


def test_proj():
    v0 = Vec2(1.0, 1.0)
    v1 = Vec2(1.0, 0.0)

    assert v0.project_onto(v1) == Vec2(1.0, 0.0)
