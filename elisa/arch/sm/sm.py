# auth: christian bitter
# name: sm.py
# desc: simple deterministic Finite State Automaton/ Machine definition
from __future__ import annotations

from uuid import uuid4

from .state import State


class StateMachine(object):
    """The state machine object, i.e. the abstract machine that executes state transitions based on external input."""

    def __init__(
        self, states: list, transitions: list, initial_state: State, final_state: State
    ):
        self._id = uuid4()
        self._init = initial_state
        self._final_state = final_state
        self._current_state = self._init
        self._states = dict([(s.id, s) for s in states.copy()])
        self._transitions = dict([(s.id, s) for s in transitions.copy()])
        self._adjacency = self.__build_adjacency_struct()
        self._on_started_handler = None
        self._on_finished_handler = None
        self._in_progress = False

    @property
    def on_started(self):
        return self._on_started_handler

    @on_started.setter
    def on_started(self, v) -> StateMachine:
        self._on_started_handler = v
        return self

    @property
    def on_finished(self):
        return self._on_finished_handler

    @on_finished.setter
    def on_finished(self, v) -> StateMachine:
        self._on_finished_handler = v
        return self

    @property
    def current(self):
        return self._current_state

    @property
    def final_state(self) -> State:
        return self._final_state

    @property
    def has_terminated(self) -> bool:
        """Determines if the state machine has potentially terminated by seeing if the
           current state is the state machine's final state.

        Returns:
                        bool: True if the machine has terminated else False.
        """
        return self._current_state == self._final_state

    def update(self, **kwargs):
        verbose = kwargs.get("verbose", False)

        if self._in_progress is False and self._current_state == self._init:
            if verbose:
                print("Starting State Machine: {}".format(self._current_state))
            self._in_progress = True
            if self._on_started_handler:
                self._on_started_handler()

        # get the transitions for the current state, call fires and see ...
        # in order to be deterministic we allow only a single firing transition,
        # although we allow multiple transitions per state -
        # but this is the job of the validate function
        firing_transition = []
        for tkey in self._transitions:
            t = self._transitions[tkey]
            if t.from_state == self._current_state:
                if t.fires(**kwargs):
                    firing_transition.append(t)

        assert len(firing_transition) <= 1

        if len(firing_transition) != 0:
            if verbose:
                print(
                    "No. transitions from current state: {} -> {} ({})".format(
                        self._current_state, firing_transition, len(firing_transition)
                    )
                )
            _firing_transition = firing_transition[0]
            _firing_transition.fire(**kwargs)
            self._current_state = _firing_transition.to_state
            self._current_state.act(**kwargs)

        if self._in_progress is True and self._current_state == self._final_state:
            if verbose:
                print("Ending State Machine: {}".format(self._current_state))
            self._in_progress = False
            if self._on_finished_handler is not None:
                self._on_finished_handler()

    @property
    def transitions(self):
        return self._transitions

    @property
    def states(self):
        return self._states

    def __build_adjacency_struct(self) -> dict:
        """Build an adjacency list from the states and transitions defined for this state machine.

        Returns:
            dict: map of state identifiers to list of state identifiers, representing the to states that can be transitioned from a source state.
        """
        _adj_struct = {}

        if len(self._states) > 0:
            for skey in self._states:
                n = self._states[skey]
                state_trans = [
                    self._transitions[tid]
                    for tid in self._transitions
                    if self._transitions[tid].from_state == n
                ]

                if n.id not in _adj_struct:
                    _adj_struct[n.id] = []
                for t in state_trans:
                    _adj_struct[n.id].append(t.to_state.id)

        return _adj_struct

    def validate(self) -> tuple:
        """Validate the state machine by checking that there are no isolate states, no duplicated states, transitions, etc.

        Returns:
            tuple: validation result composed of state (boolean) indicating success (True), and a message (str) concerning the validation
        """
        validation_result = (True, "")
        message = "Validation Failures:"

        # validate unique state names
        s_names = []
        for _sid in self._states:
            _s = self._states[_sid]
            _sn = _s.name
            if _sn in s_names:
                message = f"{message}\r\nDuplicate State Name: {_sn}"
                break
            else:
                s_names.append(_sn)

        # validate unique names in transitions
        t_names = []
        for _tid in self._transitions:
            _t = self._transitions[_tid]
            _tn = _t.name
            if _tn in t_names:
                message = f"{message}\r\nDuplicate Transition Name: {_tn}"
                break
            else:
                t_names.append(_tn)

        # Except for the for the following.
        # final nodes do not have outgoing transitions
        # the initial node is not connected, does not have an incoming transition
        # raise a validation flag.
        # the final state cannot have any connection other to itself

        # unconnected states are those that do not occur as a to_state
        all_state_ids = [s_id for s_id in self._states]

        for s_id in self._adjacency:
            to_states = [st for st in self._adjacency[s_id] if st in all_state_ids]
            for st in to_states:
                if st not in all_state_ids:
                    raise ValueError(
                        "When validating the adjancency struct, we failed to find the state: {}".format(
                            self._states[st]
                        )
                    )
                all_state_ids.remove(st)

        # the initial state will occur only, if there is a transition into it, which is not explicitly required
        initial_state_id = self._init.id
        if initial_state_id in all_state_ids:
            all_state_ids.remove(initial_state_id)

        if len(all_state_ids) > 0:
            validation_result = False
            message = "{}\r\nThe following states are isolated states (no incoming connection): {}".format(
                message, all_state_ids
            )

        t_final = self._adjacency[self._final_state.id]
        if len(t_final) > 0:
            if self._final_state.id not in t_final:
                validation_result = False
                message = (
                    f"{message}\r\nThe terminal state can only be connected to itself"
                )

        return validation_result, message
