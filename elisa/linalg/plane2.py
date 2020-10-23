from .vec2 import Vec2

class Plane2():
	"""A 2-dimensional plane provided via a surface normal vector and some offset vector
	"""
	def __init__(self, normal:Vec2, p:Vec2, normalize_direction:bool = True):
		super(Plane2, self).__init__()
		# the plane equation -> normal * x - d = 0
		# or normal (x - p) = 0 should hold for any vector on the plane, i.e.
		# perpendicular to the surface normal
		self._normal = normal.to_unit() if normalize_direction else normal
		self._p = p
		self._w = Vec2.dot(normal, p)

	@property
	def normal(self):
		return self._normal

	@property
	def w(self):
		return self._w
	
	@property
	def p(self):
		return self._p
	
	def contains(self, p:Vec2):
		m = Vec2.dot(self._normal, p)
		return m == self._w

	def __repr__(self):
		return "Plane2: {} * x - {} = 0".format(self._normal, self._w)