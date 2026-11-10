import pytest 

from elisa.linalg import angle_to_rad


def test_angle():
    assert angle_to_rad(0) == 0.