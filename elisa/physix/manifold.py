from dataclasses import dataclass, field

from ..linalg import Point2, Vec2


@dataclass
class Manifold:
    normal: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    """unit normal
    """
    depth: float = 0.0
    """penetration depth
    """
    contact: list[Point2] | None = field(default_factory=list)
    """if any, one or more contact points
    """
