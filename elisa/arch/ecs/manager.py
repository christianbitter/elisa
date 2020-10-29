from .core import ECSBase
from .ecs import Component, Entity, System


# We start with a simple manager like entity, i.e. it does not encapsulate creation/ factory
# TODO: make this a singleton
# https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html?highlight=singleton
class ECSManager(ECSBase):
	def __init__(self):
	 super(ECSManager, self).__init__()
	 self._o_map = {}

	def add(self, o) -> None:
		if o.id in self._o_map:
			raise ValueError(f"{o} already present")
		else:
			self._o_map[o.id] = o

	def remove(self, id:str) -> None:
		if not id or id == '':
			raise ValueError("id cannot be null")
		if id not in self._o_map:
			raise ValueError(f"{id} not present" )
		del(self._o_map[id])

	def get(self, id:str) -> bool:
		if not id or id == '':
			raise ValueError("id cannot be null")
		if id not in self._o_map:
			raise ValueError(f"{id} not present" )
		return self._o_map[id]

class EntityManager(ECSManager):
	def __init__(self):
	 super(EntityManager, self).__init__()

class ComponentManager(ECSManager):
	def __init__(self):
	 super(ComponentManager, self).__init__()
	 self._etype_map = {}