from __future__ import annotations

import math
from .linalg import is_numeric
from .vec3 import Point3, Vec3

# TODO: general functions ... is orthogonal, is orthonormal

class Mat3:
	"""
	A 3x3 matrix, built in row-wise order. That is the values a, b, c, d, e, f, g, h, i
	go into:
	a | b | c
	---------
	d | e | f
	---------
	g | h | i
	"""
	def __init__(self, a, b, c, d, e, f, g, h, i):
		self._v = [a, b, c, d, e, f, g, h, i]

	@property
	def shape(self):
		return 3, 3

	def __getitem__(self, i):
		if 0 <= i <= 8:
			return self._v[i]
		else:
			raise ValueError("index wrong")
	
	def __setitem__(self, i, v):
		if v == None:
			raise ValueError("v not provided")

		if 0 <= i <= 8:
			self._v[i] = v
		else:
			raise ValueError("index for assignment is outside of [0, 8]")

	def __add__(self, other):
			if is_numeric(other):
				return self.__add__(Mat3(other, other, other, other, other, other, other, other, other))
			elif isinstance(other, Mat3):
				return Mat3(self._v[0] + other[0], self._v[1] + other[1], self._v[2] + other[2],
										self._v[3] + other[3], self._v[4] + other[4], self._v[5] + other[5],
										self._v[6] + other[6], self._v[7] + other[7], self._v[8] + other[8])
			else:
				raise ValueError("other has incompatible type")

	def __sub__(self, other):
			if is_numeric(other):
				return self.__sub__(Mat3(other, other, other, other, other, other, other, other, other))
			elif isinstance(other, Mat3):
				return Mat3(self._v[0] - other[0], self._v[1] - other[1], self._v[2] - other[2],
										self._v[3] - other[3], self._v[4] - other[4], self._v[5] - other[5],
										self._v[6] - other[6], self._v[7] - other[7], self._v[8] - other[8])
			else:
				raise ValueError("other has incompatible type")

	def __mul__(self, other):
			if is_numeric(other):
					return Mat3(self._v[0] * other, self._v[1] * other, self._v[2] * other, 
											self._v[3] * other, self._v[4] * other, self._v[5] * other,
											self._v[6] * other, self._v[7] * other, self._v[8] * other)
			elif isinstance(other, Vec3):
				return Vec3(self._v[0] * other[0] + self._v[1] * other[1] + self._v[2] * other[2],
										self._v[3] * other[0] + self._v[4] * other[1] + self._v[5] * other[2],
										self._v[6] * other[0] + self._v[7] * other[1] + self._v[8] * other[2])
			elif isinstance(other, Mat3):
					v0, o0 = self._v[0], other[0]
					v1, o1 = self._v[1], other[1]
					v2, o2 = self._v[2], other[2]
					v3, o3 = self._v[3], other[3]
					v4, o4 = self._v[4], other[4]
					v5, o5 = self._v[5], other[5]
					v6, o6 = self._v[6], other[6]
					v7, o7 = self._v[7], other[7]
					v8, o8 = self._v[8], other[8]
					return Mat3(v0 * o0 + v1 * o3 + v2 * o6, v0 * o1 + v1 * o4 + v2 * o7, v0 * o2 + v1 * o5 + v2 * o8,
											v3 * o0 + v4 * o3 + v5 * o6, v3 * o1 + v4 * o4 + v5 * o7, v3 * o2 + v4 * o5 + v5 * o8,
											v6 * o0 + v7 * o3 + v8 * o6, v6 * o1 + v7 * o4 + v8 * o7, v6 * o2 + v7 * o5 + v8 * o8)

			else:
					raise ValueError("Matrix multiplication for the provided type combination not implemented")

	def __truediv__(self, other):
			if is_numeric(other):
					other_inv = 1. / other
					return self * other_inv
			else:
					return self * Mat3.inverse(other)

	@property
	def a(self):
		return self._v[0]

	@property
	def b(self):
		return self._v[1]

	@property
	def c(self):
		return self._v[2]

	@property
	def d(self):
		return self._v[3]

	@property
	def e(self):
		return self._v[4]

	@property
	def f(self):
		return self._v[5]

	@property
	def g(self):
		return self._v[6]

	@property
	def h(self):
		return self._v[7]

	@property
	def i(self):
		return self._v[8]

	@property
	def trace(self):
		return self._v[0] + self._v[4] + self._v[8]

	@property
	def diag(self):
		return [self._v[0], self._v[4], self._v[8]]

	@property
	def det(self):
		return Mat3.determinant(self)

	@property
	def inv(self):
		return Mat3.inverse(self)

	@staticmethod
	def inverse(m:Mat3):
		assert(isinstance(m, Mat3))
		d = m.det
		if d == 0.:
			raise ValueError("Matrix cannot be inverted, determinant is 0")
		d_inv = 1. / d
		# TODO: inverse
		raise ValueError("Not implemented matrix 3 inverse")

	@staticmethod
	def determinant(m):
		assert(isinstance(m, Mat3))
		# TODO: determinant
		raise ValueError("Not implemented")

	@staticmethod
	def transpose(m):
		return m.t

	@property
	def c0(self):
		return [self._v[0], self._v[3], self._v[5]]	

	@property
	def c1(self):
		return [self._v[1], self._v[4], self._v[7]]

	@property
	def c2(self):
		return [self._v[2], self._v[5], self._v[8]]

	@property
	def r0(self):
		return [self._v[0], self._v[1], self._v[2]]

	@property
	def r1(self):
		return [self._v[3], self._v[4], self._v[5]]

	@property
	def r2(self):
		return [self._v[6], self._v[7], self._v[8]]

	@property
	def t(self):
		return Mat3(self._v[0], self._v[3], self._v[6], self._v[1], self._v[4], self._v[7], self._v[2], self._v[5], self._v[8])

	def __str__(self):
		return """[Mat3]
				[{}, {}, {}
				 {}, {}, {}
				 {}, {}, {}]""".format(*self._v)

zero3 = Mat3(0., 0., 0., 0., 0., 0., 0., 0., 0.)
one3  = Mat3(1., 1., 1., 1., 1., 1., 1., 1., 1.)
eye3  = Mat3(1., 0., 0., 0., 1., 0., 0., 0., 1.)

def translate2D(x:float, y:float) -> Mat3:
	m = Mat3(1., 0., x, 0., 1., y, 0., 0., 1.)
	return m