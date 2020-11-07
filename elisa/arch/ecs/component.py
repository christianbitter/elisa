from __future__ import annotations

from .core import ECSBase

class Component(ECSBase):
	"""The Component in the ECS decomposition approach. The Component is derived from ECS base, and for that matter has assigned an internal id.
	the allow_multiple_on_entity should indicate if an entity can have multiple components of the respective type.
	However, this is not enforced at the component level but needs to be ensured by the entity or some outside entity.
	"""	
	allow_multiple_on_entity = True

	"""A component is simply a collection of state that defines an entity in the game world. Components can bind properties
	like position, velocity or health.
	Args:
			ECSBase ([type]): [description]
	"""
	def __init__(self, component_type):
		super(Component, self).__init__()
		self._component_type = component_type

	@property
	def component_type(self):
		return self._component_type

	def __repr__(self):
	 return f"[Component/ {self._component_type}]: {self._id}"

	def __str__(self):
		return self.__repr__()

	def serialize(self):
	# TODO: component serialize
	 return super().serialize()

	def deserialize(self, str):
	# TODO: component deserialize
	 return super().deserialize(str)
