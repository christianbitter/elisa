# auth: christian bitter
# name: sm.py
# desc: simple deterministic Finite State Automaton/ Machine definition
from .state import State
from uuid import uuid4

class StateMachine(object):
	"""The state machine object, i.e. the abstract machine that executes state transitions based on external input.
	"""
	def __init__(self, states: list, transitions: list, initial_state: State):
			self._id   = uuid4()
			self._init = initial_state
			self._current_state = self._init
			self._states = states.copy()
			self._transitions = transitions.copy()

	@property
	def current(self):
		return self._current_state

	def update(self, **kwargs):
		# get the transitions for the current state, call fires and see ...
		# in order to be deterministic we allow only a single firing transition, although we allow multiple transitions
		# per state - but this is the job of the validate function
		firing_transition = None
		for t in self._transitions:
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