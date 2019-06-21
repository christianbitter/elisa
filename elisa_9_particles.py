# auth: christian bitter
# desc: some particles on the screen. this is not a fully fleshed out version,
#       but it has some basic components such as moving of cooling down particles.

from random import random
import pygame as pg
import math
import time


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


def mouse_inside(mx, my, s_width, s_height):
    return mx >= 0 and my >= 0 and mx <= s_width and my <= s_height

def main():
    if not pg.font: print("Pygame - fonts not loaded")
    if not pg.mixer: print("Pygame - audio not loaded")

    pg.init()

    S_WIDTH = 640
    S_HEIGHT= 480
    S_TITLE = "Elisa9 - Particles"
    C_BLACK = (0, 0, 0)
    MAX_PARTICLES = 1000
    PARTICLE_SIZE = 3
    TEMP_DECREASE = .001
    MAX_PARTICLE_VELOCITY = (70., 70.)

    G_DIR   = _to_unit_vector(_angle_to_dir(90))
    G_FORCE = (0 * G_DIR[0], G_DIR[1] * 9.81)

    velocity = (50, 50)  # equal contribution in both
    screen_buffer = pg.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pg.display.set_caption(S_TITLE)
    pg.mouse.set_visible(True)

    back_buffer = pg.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_BLACK)

    is_done = False

    ps = ParticleSystem(max_particles=MAX_PARTICLES)

    cns = time.perf_counter_ns()
    pns = time.perf_counter_ns()

    while not is_done:
        #time_ms = pygame.time.get_ticks()
        pns = cns
        cns = time.perf_counter_ns()
        dns = cns - pns

        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_done = True

        x, y  = pg.mouse.get_pos()
        alpha = int(random() * 360)
        dir  = _to_unit_vector(_angle_to_dir(alpha))
        v = (dir[0] * velocity[0], dir[1] * velocity[1])
        if not mouse_inside(x, y, S_WIDTH, S_HEIGHT):
            x = int(random() * S_WIDTH)
            y = int(random() * S_HEIGHT)

        # we start particles of at some location with random energy/ temperature
        # you can control position, temperature, cool down, etc.
        # we want to avoid slow moving particles, so MIN_SPEED > 0
        t = random()
        p = Particle(pos=(x, y),
                     temperature=t, temp_decrease=TEMP_DECREASE, size=PARTICLE_SIZE,
                     velocity=v, max_velocity=MAX_PARTICLE_VELOCITY,
                     acceleration=G_FORCE, max_acceleration=-1)

        back_buffer.fill(C_BLACK)
        ps.add_particle(p)

        ps.update(t=dns * 1e-9)
        ps.render(back_buffer)
        screen_buffer.blit(back_buffer, (0, 0))
        pg.display.flip()

if __name__ == '__main__': main()