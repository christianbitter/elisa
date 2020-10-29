# auth: christian bitter
# name: sm.py
# desc: simple deterministic Finite State Automaton/ Machine definition

import uuid

class State(object):
    """The primary object in a state machine is the individual state of that machine. It represents a set of configurations
    that state machine possesses at given point in time.
    """
    def __init__(self, name:str, description:str = None):
        super(State, self).__init__()

        self._id   = uuid.uuid1()
        self._name = name
        self._description = description

    def __repr__(self):
        return "{} ({})".format(self._name, self._id)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __eq__(self, other):
        return other.id == self._id


class Transition(object):
    """
    Transitions in a state machine are the primary carrier of behaviour, i.e. they are responsible for moving the logical time forward in a state machine, by
    jumping from the current state to the next state assuming under the assumption of a condition holding that permits this jumping.
    """    
    def __init__(self, f: State, t: State, trigger_fn, name: str = None, description: str = None):
        super(Transition, self).__init__()
        self._id = uuid.uuid1()
        self._from = f
        self._to = t
        self._trigger = trigger_fn
        self._name = name
        self._description = description

    def __repr__(self):
        return "{} ({}) : {} => {}".format(self._id, self._name, self._from, self._to)

    def fires(self) -> bool:
        return self._trigger()

    @property
    def from_state(self):
        return self._from

    @property
    def to_state(self):
        return self._to


class StateMachine(object):
    """The state machine object, i.e. the abstract machine that executes state transitions based on external input.
    """
    def __init__(self, states: list, transitions: list, initial_state: State):
        self._id   = uuid.uuid1()
        self._init = initial_state
        self._current_state = self._init
        self._states = states.copy()
        self._transitions = transitions.copy()

        # self._validate()

    def _validate(self):
        raise ValueError("TODO:")

    @property
    def current(self):
        return self._current_state

    def update(self):
        # get the transitions for the current state, call fires and see ...
        # in order to be deterministic we allow only a single firing transition, although we allow multiple transitions
        # per state - but this is the job of the validate function
        firing_transition = None
        for t in self._transitions:
            if t.from_state == self._current_state:
                if t.fires():
                    firing_transition = t
                    break

        if firing_transition:
            self._current_state = firing_transition.to_state

    @property
    def transitions(self):
        return self._transitions

    @property
    def states(self):
        return self._states