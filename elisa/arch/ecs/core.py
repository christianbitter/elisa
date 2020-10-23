from uuid import uuid4

# https://www.gamasutra.com/blogs/TobiasStein/20171122/310172/The_EntityComponentSystem__An_awesome_gamedesign_pattern_in_C_Part_1.php#comments
# TODO: Logger
# TODO: Manager -> EntityManager, ComponentManager, EventManager

class ECSBase(object):
	"""This is the ECS base entity

	Args:
			object ([type]): [description]
	"""
	def __init__(self):
		"""Initializes the instance, setting internal id to new uuid4 value
		"""
		self._id = uuid4()

	@property
	def id(self):
		return self._id

	def __repr__(self):
		return f"ECSBase[{self.id}]"
