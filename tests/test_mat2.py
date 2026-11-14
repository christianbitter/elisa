import math

from elisa.linalg import Mat2, angle_to_rad


def test_rotation():
    m = Mat2.create_rotation(angle_to_rad(90))

    print(m[0])

    assert m.shape == (2, 2)
    assert m._v == [0, -1., 1., 0.]
