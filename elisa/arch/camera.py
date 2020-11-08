from elisa.linalg import Vec2, zero2, zero3, eye3, eye2, one2, one3, Point2, Mat2, Mat3, Point3, Vec3

class Camera2D:
	def __init__(self, ws_xmin:float, ws_xmax:float, ws_ymin:float, ws_ymax:float, vw_width:int, vw_height:int):
		"""Create a new 2D Camera.

		Args:
				ws_xmin (float): world space xmin
				ws_xmax (float): world space xmax
				ws_ymin (float): world space ymin
				ws_ymax (float): world space ymax
				vw_width (int): viewport width
				vw_height (int): viewport height
		"""
		super(Camera2D, self).__init__()
		self._ws_xmin = ws_xmin
		self._ws_xmax = ws_xmax
		self._ws_ymin = ws_ymin
		self._ws_ymax = ws_ymax
		self._ws_xrange = ws_xmax - ws_xmin
		self._ws_yrange = ws_ymax - ws_ymin

		self._nc_xmin   = -1.
		self._nc_xmax   = 1.
		self._nc_ymin   = -1.
		self._nc_ymax   = 1.
		self._nc_xrange = self._nc_xmax - self._nc_xmin
		self._nc_yrange = self._nc_ymax - self._nc_ymin

		self._vp_xmin = 0
		self._vp_xmax = vw_width
		self._vp_ymin = 0
		self._vp_ymax = vw_height
		self._vp_xrange = self._vp_xmax - self._vp_xmin
		self._vp_yrange = self._vp_ymax - self._vp_ymin

		# the individual camera components for translation, rotation and scaling
		self._m_rot   = eye3
		self._m_scale = eye3
		self._m_trans = eye3
		# the final matrix
		self._ws = eye3

		a = self._nc_xrange / self._ws_xrange
		b = -a * self._ws_xmin + self._nc_xmin
		c = self._nc_yrange / self._ws_yrange
		d = -c * self._ws_ymin + self._nc_ymin

		self._nc = Mat3(a , 0., b,
										0.,  c, d,
										0., 0., 1.)

		a = self._vp_xrange / self._nc_xrange
		b = self._vp_yrange / self._nc_yrange
		c = -self._nc_xmin * a
		d = -self._nc_ymin * b
		self._vp = Mat3(a , 0., c,
										0., b , d,
										0., 0., 1.)

	@property
	def mat_nc(self):
		return self._nc
	@property
	def mat_vp(self):
		return self._vp
	@property
	def mat_ws(self):
		return self._ws
	
	@mat_ws.setter
	def mat_ws(self, v:Mat3):
		self._ws = v

	def _update_ws(self):
		# TODO: update the ws matrix: for now we only take translation
		self._ws = self._m_trans

	def translate(self, p:Point2):
		if not p:
			raise ValueError("p? point to translate to not provided: {}".format(p))

		_update = False
		if self._m_trans[2] != p.x:
			self._m_trans[2] = p.x
			_update = True

		if self._m_trans[5] != p.y:
			self._m_trans[5] = p.y
			_update = True
		
		if _update:
			self._update_ws()

	def rotate(self, alpha_deg:float):
		raise ValueError("TODO: rotation")

	def scale(self, sx:float, sy:float):
		self._m_scale[0] = sx
		self._m_scale[4] = sy

	@property
	def position(self):
		return (self._m_trans[2], self._m_trans[5])
	
	@property
	def rotation_angle(self):
		raise ValueError("Todo")

	@property
	def scaling(self):
		return (self._m_scale[0], self._m_scale[4])

	def clip(self, x):
		# TODO: clip
		pass

	def is_visible(self, p:Point2) -> bool:
		if not p:
			raise ValueError("no point provided")
		# TODO: visibility determination
		# to start we restrict ourself to a single point in clip space
		return -1. <= p.x <= 1. and -1. <= p.y <= 1.

	def project_ws(self, x):
		"""Project points from their local coordinate system to the world coordinate system

		Args:
				x (tuple/Point2/Vec2): the point in local object space that we wish to transform

		Returns:
				Point2: the projected point
		"""
		if not x:
			raise ValueError("Missing point")
		
		p = x
		if isinstance(x, tuple):
			p = Point3(x[0], x[1], 1.)
		elif isinstance(x, Vec2):
			p = Point3(x.x, x.y, 1.)
		elif isinstance(x, Point3):
			pass
		else:
			raise ValueError("Undefined type provided: {}".format(type(x)))

		projected = self._ws * p
		return Point2(projected.x, projected.y)

	def project_nc(self, ws_x) -> Point2:
		"""Projects a point from world space into the normalized clip space.

		Args:
				ws_x (tuple/Point2/Vec2): the point in world space that we wish to transform

		Raises:
				ValueError: no point provided.

		Returns:
				Point2: the transformed point
		"""
		if not ws_x:
			raise ValueError("point not provided")

		p = ws_x
		if isinstance(ws_x, tuple):
			p = Point3(ws_x[0], ws_x[1], 1.)
		elif isinstance(ws_x, Vec2):
			p = Point3(ws_x.x, ws_x.y, 1.)
		elif isinstance(ws_x, Point3):
			pass			
		else:
			raise ValueError("Undefined type provided")

		projected = self._nc * p
		return Point2(projected.x, projected.y)

	def project_vp(self, nc_x):
		"""Projects a point from normalized clip space into the viewport/ device space

		Args:
				nc_x (tuple/Point2/Vec2): the point in nc space that we wish to transform

		Raises:
				ValueError: no point provided.

		Returns:
				Point2: the transformed point
		"""
		if not nc_x:
			raise ValueError("point not provided")

		p = nc_x
		if isinstance(nc_x, tuple):
			p = Point3(nc_x[0], nc_x[1], 1.)
		elif isinstance(nc_x, Vec2):
			p = Point3(nc_x.x, nc_x.y, 1.)
		elif isinstance(nc_x, Point3):
			pass			
		else:
			raise ValueError("Undefined type provided")

		projected = self._vp * p
		return Point2(projected.x, projected.y)