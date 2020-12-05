from __future__ import annotations
from uuid import uuid4


class State(object):
    """The primary object in a state machine is the individual state of that machine. It represents a set of configurations
    that state machine possesses at given point in time.
    """

    def __init__(self, name: str, description: str = None):
        super(State, self).__init__()

        self._id = uuid4()
        self._name = name
        self._description = description

    def __repr__(self):
        return "{} ({})".format(self._name, self._id)

    def act(self, **kwargs):
        """When entering the state, this function is executed"""
        pass

    @property
    def id(self) -> str:
        """Gets the state's id.

        Returns:
                        str: the state id
        """
        return str(self._id)

    @property
    def name(self) -> str:
        """Gets the state's name.

        Returns:
                        uuid4: the state name
        """
        return self._name

    @name.setter
    def name(self, v: str) -> State:
        self._name = v
        return self

    @property
    def description(self) -> str:
        """Gets the state's description.

        Returns:
                        uuid4: the state description
        """
        return self._description

    @description.setter
    def description(self, v: str) -> State:
        self._description = v
        return self

    def __eq__(self, other: State):
        return other.id == self.id
