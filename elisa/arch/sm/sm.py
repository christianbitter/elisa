# auth: christian bitter
# name: sm.py
# desc: simple deterministic Finite State Automaton/ Machine definition
from .state import State
from uuid import uuid4

class StateMachine(object):
	"""The state machine object, i.e. the abstract machine that executes state transitions based on external input.
	"""
	def __init__(self, states: list, transitions: list, initial_state:State, final_state:State):
			self._id   = uuid4()
			self._init = initial_state
			self._final_state   = final_state
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
		l = {}

		if len(self._states) > 0:
			for skey in self._states:
				n = self._states[skey]
				state_trans = [self._transitions[tid] for tid in self._transitions if self._transitions[tid].from_state == n]				
				
				if n.id not in l:
					l[n.id] = []
				for t in state_trans:
					l[n.id].append(t.to_state.id)

		return l

	def validate(self) -> tuple:		
		validation_result = True,
		message = "All ok"
		
		# Except for the final node, if there is any other isolated node,
		# raise a validation flag.
		# the final state cannot have any connection other to itself

		# unconnected states are those that do not occur as a to_state
		all_state_ids = [s_id for s_id in self._states]

		for s_id in self._adjacency:
			to_states = [st for st in self._adjacency[s_id] if st in all_state_ids]
			for st in to_states:
				all_state_ids.remove(st)

		if len(all_state_ids) > 0:
			validation_result = False
			message = "The following states are isolated states (no incoming connection): {}".format(all_state_ids)
				
		t_final = self._adjacency[self._final_state.id]
		if len(t_final) > 0:
			if not self._final_state.id in t_final:
				validation_result = False
				message = "The terminal state can only be connected to itself"

		return validation_result, message