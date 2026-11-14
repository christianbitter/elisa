"""Physics primitives for Elisa.

The roadmap implemented here is the learning project
``game-physics-for-my-own-2d-engine-python``.  M1 is scaffolded; later
milestones add collision, broad phase, the impulse solver and continuous
collision to this package.
"""

from .accumulator import FixedStepAccumulator
from .body import Body
from .constants import (
    CORRECTION_FRACTION,
    FIXED_DT,
    GRAVITY_Y,
    MAX_FRAME_TIME,
    RESTITUTION_THRESHOLD,
    SLOP,
    SOLVER_ITERATIONS,
)
from .physics import force, gravitational_force, weight
from .world import World

__all__ = [
    "CORRECTION_FRACTION",
    "FIXED_DT",
    "GRAVITY_Y",
    "MAX_FRAME_TIME",
    "RESTITUTION_THRESHOLD",
    "SLOP",
    "SOLVER_ITERATIONS",
    "Body",
    "FixedStepAccumulator",
    "World",
    "force",
    "gravitational_force",
    "weight",
]
