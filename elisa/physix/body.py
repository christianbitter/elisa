from dataclasses import dataclass, field

from ..linalg import Vec2


@dataclass
class Body:
    """A point mass for M1.

    Attributes:
        position: Centre position in world space (Vec2, metres).
        velocity: Linear velocity (Vec2, m/s).
        acceleration: Acceleration accumulated for the *current* step only
            (Vec2, m/s^2); the world clears it after integrating.  Gravity is
            supplied by the world and is not stored here.
        inv_mass: Inverse mass (1/kg).  Use 0.0 for an immovable body; M3
            relies on this rather than a special case.
        is_static: Whether the body is immovable.  M1 skips static bodies.
    """

    position: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    acceleration: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    inv_mass: float = 1.0
    is_static: bool = False
