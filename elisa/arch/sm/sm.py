# auth: christian bitter
# name: sm.py
# desc: simple deterministic Finite State Automaton/ Machine definition
from .state import State
from uuid import uuid4


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
        # get the transitions for the current state, call fires and see ...
        # in order to be deterministic we allow only a single firing transition, although we allow multiple transitions
        # per state - but this is the job of the validate function
        firing_transition = None
        for tkey in self._transitions:
            t = self._transitions[tkey]
            if t.from_state == self._current_state:
                if t.fires(**kwargs):
                    firing_transition = t
                    break

        if firing_transition:
            firing_transition.fire(**kwargs)
            self._current_state = firing_transition.to_state
            self._current_state.act(**kwargs)

    @property
    def transitions(self):
        return self._transitions

    @property
    def states(self):
        return self._states

    def __build_adjacency_struct(self):
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
