class Manager():
	def __init__(self):	 
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