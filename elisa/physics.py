def force(m: float, a):
    """
    force applied to an object is proportional to the object's mass and acceleration
    :param m: (float) object mass
    :param a: object acceleration
    :return: the net force
    """
    return m * a

def weight(m: float, gravitational_force: float) -> float:
    return m * gravitational_force


class constants:
    """"""

    def __init__(self, ):
        """Constructor for constants"""
        super(constants, self).__init__()

    """
    Gravitional constant G
    """
    G: float = 6.674e-11  # N * m^2/ kg^2

    Mass_Earth: float = 5.9736e+24  # kg
    Radius_Earth: float = 6.375e+6  # m


def gravitational_force(m1:float, m2:float, r:float):
    return constants.G * m1 * m2 / r**2
