from enum import Enum
from .arch.ecs import Entity


class PlayerType(Enum):
	"""
	Enumeration of different player types.
	"""
	CPU = 1
	Human = 2

	def __str__(self):
			return self.name


class Player(Entity):
	"""
	A player entity
	"""

	def __init__(self, name: str, p_type: PlayerType):
		"""Constructor for Player"""
		super(Player, self).__init__(name=name)
		self._type = p_type

	def __str__(self):
		return "[{}] {}".format(self._id, self._name)

	def __eq__(self, other):
		return self._id == other.id

	@property
	def player_type(self):
		return self._type

	def __repr__(self):
		return "{} ({}: {})".format(self._name, self._type, self._id)
