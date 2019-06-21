# auth: christian bitter
# name: particle.py
# desc: a collection of types and functions to build a small particle system
# TODO: time-based integrator in a future version
# TODO: better physics integration, update decoupling, render decoupling
# TODO: allow for bitmaps/ gfx to be particles
# TODO: enable alpha channel modification
# TODO: separation of particle/particle system into data and rendering

import pygame as pg


class Particle(object):
    """
    The particle is some object moving around in space. it is visible due to the heat it emits.
    Over time the particle cools down until it is cold. A cold particle does not emit energy/light.
    """
    def __init__(self, pos, size: int,
                 temperature:float, temp_decrease,
                 velocity, max_velocity, acceleration, max_acceleration):
        """Constructor for Particle"""
        super(Particle, self).__init__()
        self._pos = pos
        self._size = size
        self._temperature = temperature
        self._velocity = velocity
        self._max_velocity = max_velocity
        self._acceleration = acceleration
        self._max_acceleration = max_acceleration
        self._temperature_decrease = temp_decrease

    @property
    def size(self):
        return self._size

    @property
    def direction(self):
        return self._dir

    @property
    def x(self):
        return self._pos[0]

    @property
    def y(self):
        return self._pos[1]

    @property
    def temperature(self):
        return self._temperature

    @property
    def velocity(self):
        return self._velocity

    @property
    def acceleration(self):
        return self._acceleration

    @property
    def is_hot(self):
        return self._temperature > 0

    def update(self, t=1.):
        # cool down
        self._temperature = max(self._temperature - self._temperature_decrease, 0)

        # move in a simple way
        vx = self._velocity[0] + self._acceleration[0] * t
        vy = self._velocity[1] + self._acceleration[1] * t
        x = self._pos[0] + vx * t
        y = self._pos[1] + vy * t
        self._velocity = (vx, vy)
        self._pos = (x, y)

    def __repr__(self):
        x, y = self._pos[0], self._pos[1]
        vx, vy = self._velocity[0], self._velocity[1]
        ax, ay = self._acceleration[0], self._acceleration[1]
        return "Particle ({}, {}) = {}\r\n{}\r\n{}".format(x, y, self._temperature,
                                                           "(x, vx, ax): {}, {}, {}".format(x, vx, ax),
                                                           "(y, vy, ay): {}, {}, {}".format(y, vy, ay))


class ParticleSystem(object):
    """"""

    def temperature2colour(temperature):
        return (int(temperature*255), 0, int(temperature*128))

    def __init__(self, max_particles):
        """Constructor for ParticleSystem"""
        super(ParticleSystem, self).__init__()
        self._max_particles = max_particles
        self._particles = []

    def add_particle(self, p: Particle):
        if not p:
            raise ValueError("Particle p missing")
        if len(self._particles) < self._max_particles:
            self._particles.append(p)

    @property
    def particles(self):
        return self._particles

    def update(self, t=1.):
        removes = []
        for p in self._particles:
            p.update(t)
            if not p.is_hot:
                removes.append(p)

        for x in removes:
            self._particles.remove(x)

    def render(self, buffer):
        w = buffer.get_width()
        h = buffer.get_height()

        for p in self._particles:
            col = ParticleSystem.temperature2colour(p.temperature)
            if p.x < w and p.y < h and p.x >= 0 and p.y >= 0:
                pg.draw.circle(buffer, col, (int(p.x), int(p.y)), p.size, 0)
