import sys
from math import floor, ceil
from .linalg import lerp1D
# https://mzucker.github.io/html/perlin-noise-math-faq.html
# http://staff.fh-hagenberg.at/burger/publications/reports/2008GradientNoise/Burger-GradientNoiseGerman-2008.pdf


def perlin_noise(x, y=None):

    def ease_curve(p):
        return (3. * (p**2.)) - (2. * (p**3.))

    def g1(x_:int):
        """
        one dimensional pseudo-random gradient vector function. mapping values from [0, n] to [-1, 1]
        :param x_:
        :return:
        """
        if x_ == 0.:
            return -1
        return 2. * (1. / hash(x_)) - 1.

    def g2(x_, y_):
        pass

    def pnoise1(x_):
        x0 = floor(x_)
        x1 = ceil(x_)
        gx0, gx1 = g1(x0), g1(x1)
        xx0 = x_ - x0
        xx1 = x_ - x1
        # similarity between the pseudo-random gradient and the vector to x determines the influence
        # of the pseudo-random vector on the final blending
        s = gx0 * xx0
        t = gx1 * xx1
        s_x = ease_curve(x_ - x0)
        a = lerp1D(s, t, s_x)
        return a

    def pnoise2(x_, y_):
        x0, x1, y0, y1 = floor(x_), ceil(_x), floor(y_), ceil(y_)
        pass

    if x is None:
        raise ValueError("x cannot be None")
    if y is None:
        return pnoise1(x)
    else:
        return pnoise2(x, y)
