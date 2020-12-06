from __future__ import annotations

from uuid import uuid4
from .state import State


class Transition(object):
    """
    Transitions in a state machine are the primary carrier of behaviour, i.e. they are responsible for moving the logical time forward in a state machine, by
    jumping from the current state to the next state assuming under the assumption of a condition holding that permits this jumping.
    """

    def __init__(
        self,
        f: State,
        t: State,
        trigger_fn,
        on_fire_handler=None,
        name: str = None,
        description: str = None,
    ):
        """[summary]

        Args:
                        f (State): The from state
                        t (State): The to state
                        trigger_fn (function(**kwargs) -> boolean): A function returning true if the transition fires else False
                        on_fire_handler (function(from:State, to:State, **kwargs) -> None): A function that is executed on firing
                        name (str, optional): Transition Name. Defaults to None.
                        description (str, optional): Transition description. Defaults to None.
        """
        super(Transition, self).__init__()
        self._id = uuid4()
        self._from = f
        self._to = t
        self._trigger = trigger_fn
        self._name = name
        self._description = description
        self._on_fire = on_fire_handler

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def __repr__(self):
        return "{} ({}) : {} => {}".format(self._id, self._name, self._from, self._to)

    def fires(self, **kwargs) -> bool:
        return self._trigger(**kwargs)

    def fire(self, **kwargs):
        if self._on_fire:
            return self._on_fire(self._from, self._to)

    def __eq__(self, other: Transition) -> bool:
        return self.id == other.id

    @property
    def from_state(self):
        return self._from

    @property
    def to_state(self):
        return self._to

    @staticmethod
    def from_many(f: list, t: State, trigger_fn, on_fire_handler, name=None, desc=None):
        # TODO: we allow the to state to be connected from many source states, such as a final state that is fanned in from
        # all the relevant input states
        pass

    @staticmethod
    def to_many(f: State, t: list, trigger_fn, on_fire_handler, name=None, desc=None):
        # TODO: we allow to have the from state connect to many to states
        # in this case we may use trigger_fn, on_fire_handler, name, desc is one
        # or it has to have the same cardinality as the t list
        pass
