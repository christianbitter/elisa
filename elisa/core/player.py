from __future__ import annotations

from ..arch.ecs import Entity
from .core import PlayerType


class Player(Entity):
    """
    A player entity
    """

    def __init__(self, name: str, p_type: PlayerType, parent=None, **kwargs):
        """Create a new player instance

        Args:
            name (str): name of the player
            p_type (PlayerType): type of the player human or computer-controlled.
            parent (optional): parent of this player.
        """
        super(Player, self).__init__(parent=parent, **kwargs)
        self._type = p_type
        self._name = name

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self._id == other.id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, n: str) -> Player:
        if n is None or n.strip() == "":
            raise ValueError("Name not provided")

        self._name = n
        return self

    @property
    def player_type(self) -> PlayerType:
        return self._type

    def __repr__(self):
        return "Player({}: {}) {}".format(self._id, self._type, self._name)
