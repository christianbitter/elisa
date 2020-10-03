#desc: this is a simple example demonstrating some linear algebra
# such as vector addition and linear interpolation
from elisa import Vec2, Mat2

def main():
    v0 = Vec2(0, 0)
    v1 = Vec2(1, 1)
    v2 = Vec2(2, 2)
    m1 = Mat2(1, 0, 0, 1)

    print("Is {} the zero vector ? {}".format(v0, Vec2.is_zero(v0)))
    print("Length({})-{}: {}".format(v0, v0.dim, v0.length))
    print("Is {} the zero vector ? {}".format(v1, Vec2.is_zero(v1)))
    print("Length({})-{}: {}".format(v1, v1.dim, v1.length))
    print("Is {} the zero vector ? {}".format(v2, Vec2.is_zero(v2)))
    print("{} + {} = {}".format(v0, v1, v0 + v1))
    print("{} - {} = {}".format(v1, v0, v1 - v0))
    print("{} * {} = {}".format(v1, v0, v1 * v0))
    print("{} / {} = {}".format(v2, v1, v2 / v1))
    # TODO:
    print("Lerp {}, {}, {} => {}".format(0.5, v0, v2, Vec2.lerp(v0, v2, .5)))
    print("matrix 2D: {}".format(m1))
    print("Trace/ Determinant/ Inverse/ Transpose: {}, {}\r\nInverse: {}\r\nTranspose: {}".format(m1.trace, m1.det, m1.inv, m1.t))


if __name__ == '__main__':
    main()
