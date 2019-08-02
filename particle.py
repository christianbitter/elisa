# auth: christian bitter
# name: particle.py
# desc: a collection of types and functions to build a small particle system.
#   Separates data, system and rendering through Particle, ParticleSystem and ParticleSystemRenderer.
#   Allows for bitmaps/ gfx to be particles through a customer renderer.
# TODO: better physics integration - force equation and integration handling
# TODO: check how to enable the alpha blending

import pygame as pg
import math


def _to_unit_vector(v):
    vx = v[0]
    vy = v[1]
    mag = math.sqrt(vx*vx + vy*vy)
    return vx / mag, vy / mag


def alpha2rad(alpha):
    return (alpha * math.pi) / 180.


def _angle_to_dir(angle):
    angle = alpha2rad(angle)
    return math.cos(angle), math.sin(angle)


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

    @temperature.setter
    def temperature(self, t: float):
        if t is None:
            raise ValueError("temperature cannot be none")
        self._temperature = t

    @property
    def velocity(self):
        return self._velocity

    @property
    def acceleration(self):
        return self._acceleration

    @property
    def is_hot(self):
        return self._temperature > 0

    def update(self, t):
        if t < 0:
            raise ValueError("Negative time ({} s) not supported".format(t))
        if t == 0:
            return

        # cool down
        self._temperature = max(self._temperature - t * self._temperature_decrease, 0)

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
    """
    The ParticleSystem object is the main interaction point for you to spawn particles,
    render them, etc.
    """

    def __init__(self, max_particles):
        """Constructor for ParticleSystem"""
        super(ParticleSystem, self).__init__()
        self._max_particles = max_particles
        self._particles = []
        self._on_particle_died = None

    def add_particle(self, p: Particle):
        if not p:
            raise ValueError("Particle p missing")
        if self._max_particles <= 0 or len(self._particles) < self._max_particles:
            self._particles.append(p)

    def remove_particle(self, idx: int):
        if len(self._particles) < 1:
            raise ValueError("Nothing to remove")
        p = self[idx]
        self._particles.remove(p)

    @property
    def particles(self):
        return self._particles

    def __getitem__(self, item: int):
        if not (0 <= item < len(self._particles)):
            raise ValueError("item out of range")
        return self._particles[item]

    @property
    def max_particles(self):
        return self._max_particles

    def update(self, t) -> None:
        """
        Update the particle
        :param t: time t in seconds
        :return: None
        """
        if t < 0:
            raise ValueError("Negative time ({} s) not supported".format(t))
        if t == 0 or len(self._particles) < 1:
            return

        removes = []
        for p in self._particles:
            p.update(t)
            if not p.is_hot:
                removes.append(p)

        for x in removes:
            if self._on_particle_died:
                self._on_particle_died(self, x)
            self._particles.remove(x)

    @property
    def on_particle_died(self):
        """
        The on_particle_died eventhandler function is called whenever a particle is being removed,
        because it died (temperature fell below threshold, i.e. it is not hot
        :return: function f(particle_system, dying_particle) -> None
        """
        return self._on_particle_died

    @on_particle_died.setter
    def on_particle_died(self, event_handler_fn):
        """
        This allows you to set the on_particle_died eventhandler function, so that you can act whenever
        a particle has expired
        :param event_handler_fn: function f(particle_system, dying_particle) -> None
        :return:
        """
        if not event_handler_fn:
            raise ValueError("event_handler_fn missing")
        self._on_particle_died = event_handler_fn


class Renderer:
    """"""
    def __init__(self):
        """Constructor for Renderer"""
        super(Renderer, self).__init__()

    def render(self, buffer, render_items: list, x: int = None, y: int = None):
        pass


class ParticleSystemRenderer(Renderer):
    """
    """

    def __init__(self):
        """Constructor for ParticleSystemRenderer"""
        super(ParticleSystemRenderer, self).__init__()

    def temperature2colour(self, temperature:float) -> tuple:
        """
        converts the particle's temperature into a displayable colour
        :return: a 4-tuple representing an RGBA colour
        """
        return int(temperature*255), 0, int(temperature*128), 255

    def render(self, buffer, render_items: list, x: int = None, y: int = None):
        if not render_items or len(render_items) < 1:
            return

        w, h = buffer.get_width(), buffer.get_height()
        p = [0, 0]
        if x is not None:
            if not (0 <= x < w):
                raise ValueError("x outside of viewport")
            p[0] = x
        if y is not None:
            if not (0 <= y < h):
                raise ValueError("y outside of viewport")
            p[1] = y

        for particle in render_items:
            col = self.temperature2colour(particle.temperature)
            if len(col) != 4:
                raise ValueError("temperature2colour must yield an RGBA tuple")
            if 0 <= particle.x < w and 0 <= particle.y < h:
                pg.draw.circle(buffer, col, (int(particle.x), int(particle.y)), particle.size, 0)
