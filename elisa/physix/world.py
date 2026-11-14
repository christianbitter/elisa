"""M1: the fixed-step world and semi-implicit Euler integration.

This is the engine-side home of the first milestone.  The learning project
``game-physics-for-my-own-2d-engine-python`` keeps the experiment scripts,
tests and checkpoint evidence; this module keeps the reusable code.

Units are metres, seconds and kilograms throughout.  Vectors are the existing
:class:`elisa.linalg.Vec2` type, not a second vector implementation.
"""

from __future__ import annotations

from ..linalg import Vec2
from .body import Body


class World:
    """Owns one fixed timestep and the bodies simulated with it."""

    def __init__(self, dt: float = 1.0 / 60.0, gravity: Vec2 | None = None) -> None:
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        self._dt = float(dt)
        self._gravity = Vec2(0.0, 0.0) if gravity is None else Vec2(gravity)
        self._bodies: list[Body] = []

    @property
    def dt(self) -> float:
        """The fixed simulation timestep in seconds."""
        return self._dt

    @property
    def gravity(self) -> Vec2:
        return self._gravity

    @gravity.setter
    def gravity(self, value: Vec2) -> None:
        self._gravity = Vec2(value)

    @property
    def bodies(self) -> list[Body]:
        return self._bodies

    def add(self, body: Body) -> Body:
        self._bodies.append(body)
        return body

    def step(self) -> None:
        """Advance every dynamic body by exactly one fixed step.

        (M1): implement semi-implicit Euler.

        For each body that is not static:
            1. form the step acceleration from the body's accumulated
               acceleration plus this world's gravity;
            2. update velocity from that acceleration;
            3. update position from the *new* velocity;
            4. clear the body's accumulated acceleration.

        Use ``self._dt`` only: a fixed step is the point of the milestone.
        """
        dt = self._dt
        g = self._gravity

        for body in self._bodies:
            if body.is_static:
                continue

            # decide implicit - go a, v, y
            v0 = body.velocity
            y0 = body.position

            body.acceleration = body.acceleration + g
            body.velocity = v0 + body.acceleration * dt
            body.position = y0 + body.velocity * dt

            body.acceleration = Vec2(0.0, 0.0)  # clear for next step
