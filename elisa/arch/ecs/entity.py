from __future__ import annotations
from .core import ECSBase

class Entity(ECSBase):
	"""An entity is a named collection of components. You can add, remove, or search for components that the entity has registered. Additionally,
	entities can send messages to other entities and receive messages from other objects.
	"""		
	def __init__(self):
		self._components = dict()
		self._ctypes = dict()

		super(Entity, self).__init__()

	def add(self, c:Component):
		"""Add a component to an entity. Only one component per type is allowed on an entity.

		Args:
				c (Component): Component to register

		Raises:
				ValueError: if the component is not provided/ is None
				ValueError: if the component has been registered before

		Returns:
				[Entity]: the entity
		"""
		if not c:
			raise ValueError("No component provided")
		cid   = str(c._id)
		if cid in self._components:
			raise ValueError("Component already exists")

		ctype = c._component_type		
		self._components[str(c._id)] = c
		self._ctypes[ctype] = c
		
		return self

	def __getitem__(self, key):
		if isinstance(key, int):
			if key > len(self._components):
				raise ValueError("index outside of registered components")
			for i, k in enumerate(self._components):
				if i == key:
					return self._components[k]
		else:
			return self._components[key]

	def get_of_type(self, component_type:str):
		if not component_type:
			raise ValueError("component_type not provided")
		ci = self._ctypes[component_type]
		return ci

	def has_component_type(self, component_type):
		if not component_type or component_type == "":
			raise ValueError("component_type not provided")

		return component_type in self._ctypes

	def remove(self, component_id:str):
		if not component_id or component_id == "":
			raise ValueError("No component id provided")
		
		if component_id in self._components:
			ctype = self._components[component_id]._component_type
			delattr(self._components, component_id)
			delattr(self._ctypes[ctype], component_id)

		# support chaining
		return self

	def send_msg(self, msg:Message):
		pass

	def __repr__(self):		
		c_str = f"Entity: {self._id}\r\n"
		if len(self._components) == 0:
			c_str += "No registered components"
		else:
			for i, k in enumerate(self._components):
				c_str += "[+{}] = {}\r\n".format(i, self._components[k])
		return c_str

	def __str__(self):
		return self.__repr__()
