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
        """Generates a new transition from the f to the t state. The transition will happen if the trigger function is true. When the transition happens then the  on_fire_handler will fire.
        Each transition can have a name and an associated description.

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
        if not f:
            raise ValueError("From state not provided")
        if not t:
            raise ValueError("To State not provided")
        self._from = f
        self._to = t
        self._trigger = trigger_fn
        self._name = (
            name
            if name is not None and name.strip() != ""
            else "T_{}-{}".format(f.name, t.name)
        )
        self._description = (
            description
            if description is not None and description.strip() != ""
            else "Autogenerated"
        )
        self._on_before_fire_fn = None
        self._on_after_fire_fn = None
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

    @property
    def on_before_fire(self):
        return self._on_before_fire_fn

    @property
    def on_after_fire(self):
        return self._on_after_fire_fn

    @on_before_fire.setter
    def on_before_fire(self, v) -> Transition:
        self._on_before_fire_fn = v
        return self

    @on_after_fire.setter
    def on_after_fire(self, v) -> Transition:
        self._on_after_fire_fn = v
        return self

    def __eq__(self, other: Transition) -> bool:
        return self.id == other.id

    @property
    def from_state(self):
        return self._from

    @property
    def to_state(self):
        return self._to

    @staticmethod
    def from_many(
        f: list,
        t: State,
        trigger_fn,
        on_fire_handler,
        name: list = None,
        desc: list = None,
    ) -> list:
        """Generates transitions from any of the states in the from list f to the target to state t. All transitions share the same trigger function,
        and the same on_fire_handler. Each transition has its own unique name and its own description. Here the user can supply individual names and descriptions
        which have to match the number of elements in f. If you supply None for name or desc, either name or description will be auto-generated.

        Args:
            f (list): The list of source states
            t (State): The destination or target state
            trigger_fn (function(**kwargs) -> boolean): A function returning true if the transition fires else False
            on_fire_handler (function(from:State, to:State, **kwargs) -> None): A function that is executed on firing
            name (list, optional): name of transition. Defaults to None.
            desc (list, optional): description of transition. Defaults to None.

        Raises:
            ValueError: raises error if no from state or to state is provided. raises error if the name or description supplied do not match.

        Returns:
            list: list of generated transitions
        """
        if not f or len(f) < 1:
            raise ValueError("from state not provided")
        if not t:
            raise ValueError("to State note provided")

        if f and name and isinstance(name, list) is False:
            raise ValueError(
                "when using multiple from states, the name argument has to be a list of names of equal size"
            )
        if f and desc and isinstance(desc, list) is False:
            raise ValueError(
                "when using multiple from states, the desc argument has to be a list of names of equal size"
            )

        if not name:
            name = ["T_{}-{}".format(_state.name, t.name) for _state in f]

        if not desc:
            desc = ["Autogenerated"] * len(f)

        if len(f) != len(desc):
            raise ValueError("Length of descriptin and from states do not match")
        if len(f) != len(name):
            raise ValueError("Length of name and from states do not match")

        return [
            Transition(_state, t, trigger_fn, on_fire_handler, name[i], desc[i])
            for i, _state in enumerate(f)
        ]

    @staticmethod
    def to_many(f: State, t: list, trigger_fn, on_fire_handler, name=None, desc=None):
        # TODO: we allow to have the from state connect to many to states
        # in this case we may use trigger_fn, on_fire_handler, name, desc is one
        # or it has to have the same cardinality as the t list
        pass
