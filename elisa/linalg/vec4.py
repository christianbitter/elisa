import math

from .linalg import is_numeric

class Vec4:
	"""[summary]
	A simple 4D vector class to represent things like homogenous coordinates or rgba quadruples.
	"""
	def __init__(self, a=0., b=0., c=0., d=0.):
		self._v = [float(a), float(b), float(c), float(d)]

	def __repr__(self):
		return "Vec4[{}, {}, {}, {}]".format(self._v[0], self._v[1], self._v[2], self._v[3])

	@staticmethod
	def is_zero(v):
		return v[0] == 0. and v[1] == 0. and v[2] == 0. and v[3] == 0.

	def __add__(self, other):
		"""Component-wise addition of two 4-dimensional vectors.

		Args:
				other (Vec4): The vector to add to this instance

		Returns:
				Vec4: The newly created vector that results from component-wise vector addition.
		"""
		return Vec4(self._v[0] + other[0], self._v[1] + other[1], self._v[2] + other[2], self._v[3] + other[3])

	def __sub__(self, other):
		"""Component-wise subtraction of two 4-dimensional vectors.

		Args:
				other (Vec4): The vector to subtract from this instance

		Returns:
				Vec4: The newly created vector that results from component-wise vector subtraction.
		"""
		return Vec4(self._v[0] - other[0], self._v[1] - other[1], self._v[2] - other[2], self._v[3] - other[3])

	def __neg__(self):
		return Vec4(-self._v[0], -self._v[1], -self._v[2], -self._v[3])


	@staticmethod
	def dot(u, v):
		return u[0] * v[0] + u[1] * v[1] + u[2] * v[2] + u[3] * v[3]

	@staticmethod
	def mul(u, v):
		if isinstance(u, Vec4) and is_numeric(v):
			return Vec4(u[0] * v, u[1] * v, u[2] * v, u[3] * v)
		if is_numeric(u) and isinstance(v, Vec3):
			return Vec4.mul(v, u)
		if isinstance(u, Vec4) and isinstance(v, Vec4):
			return Vec4(u[0] * v[0], u[1] * v[1], u[2] * v[2], u[3] * v[3])
		raise ValueError("u and v must be numeric or Vec4 types")

	@staticmethod
	def div(u, v):
		if isinstance(u, Vec4) and is_numeric(v):
			vinv = 1. / v
			return Vec4(u[0] * vinv, u[1] * vinv, u[2] * vinv, u[3] * vinv)
		if is_numeric(u) and isinstance(v, Vec4):
			return Vec4.div(v, u)
		if isinstance(u, Vec4) and isinstance(v, Vec4):
			return Vec4(u[0] / v[0], u[1] / v[1], u[2] / v[2], u[3] / v[3])
		raise ValueError("u and v must be numeric or Vec4 types")

	def __mul__(self, other):
		return Vec4.mul(self, other)

	def __truediv__(self, other):
		return Vec4.div(self, other)

	@property
	def w(self):
		return self._v[0]

	@property
	def x(self):
		return self._v[1]

	@property
	def y(self):
		return self._v[2]

	@property
	def z(self):
		return self._v[3]

	def __getitem__(self, a):
		_a, _b = None, None
		if isinstance(a, int):
			_a, _b = a, a
			if a < 0 or a > 3:
					raise ValueError("a outside of bounds")
		if isinstance(a, slice):
			_a, _b = a.start, a.stop
			if a.start > a.stop or a.stop > 3:
					raise ValueError("upper index outside of bounds or invalid")
		if _a == _b:
			return self._v[_a]
		else:
			return self._v[_a:_b]

	@staticmethod
	def magnitude(u):
		_w = u.w
		_x = u.x
		_y = u.y
		_z = u.z
		return math.sqrt(_w**2 + _x**2 + _y**2 + _z**2)

	@staticmethod
	def unit_vector(u):
		l = Vec4.magnitude(u)
		linv = 1./l
		return u * linv

	@staticmethod
	def lerp(u, v, t: float):
		assert(isinstance(u, Vec4))
		assert(isinstance(v, Vec4))

		w = v - u
		return u + (w * t)

	def __setitem__(self, a, c):
		_a, _b = None, None
		if isinstance(a, int):
			_a, _b = a, a
			if a < 0 or a > 3:
				raise ValueError("a outside of bounds")
		if isinstance(a, slice):
			_a, _b = a.start, a.stop
			if a.start > a.stop or a.stop > 3:
				raise ValueError("upper index outside of bounds or invalid")
		if _a == _b:
			self._v[_a] = c
		else:
			self._v[_a:_b] = c


zero4 = Vec4(0, 0, 0, 0)
one3 = Vec4(1, 1, 1, 1)
