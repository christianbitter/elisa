from uuid import uuid4
from .state import State

class Transition(object):
	"""
	Transitions in a state machine are the primary carrier of behaviour, i.e. they are responsible for moving the logical time forward in a state machine, by
	jumping from the current state to the next state assuming under the assumption of a condition holding that permits this jumping.
	"""    
	def __init__(self, f: State, t: State, trigger_fn, on_fire_handler, name:str=None, description:str=None):
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

	def __repr__(self):
		return "{} ({}) : {} => {}".format(self._id, self._name, self._from, self._to)

	def fires(self, **kwargs) -> bool:
		return self._trigger(**kwargs)

	def fire(self, **kwargs):
		if self._on_fire:
			self._on_fire(self._from, self._to)

	@property
	def from_state(self):
		return self._from

	@property
	def to_state(self):
		return self._to