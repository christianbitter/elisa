from __future__ import annotations
from uuid import uuid4

# https://www.gamasutra.com/blogs/TobiasStein/20171122/310172/The_EntityComponentSystem__An_awesome_gamedesign_pattern_in_C_Part_1.php#comments
# TODO: Logger
# TODO: Manager -> EntityManager, ComponentManager, EventManager


class ECSBase(object):
    """This is the ECS base entity. It consists of a uuid4 instance to track object identities."""

    def __init__(self, **kwargs):
        """Create a new instance."""
        self._id = uuid4()

    @property
    def id(self) -> uuid4:
        return self._id

    def __repr__(self) -> str:
        return f"ECSBase[{self.id}]"

    def __str__(self) -> str:
        return self.__repr__()

    def serialize(self) -> str:
        raise ValueError("serialize not implemented")

    def deserialize(self, str) -> ECSBase:
        raise ValueError("deserialize not implemented")
