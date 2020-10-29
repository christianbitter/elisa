class Camera:
	"""
	Abstract camera
	"""
	def __init__(self):
		pass

	def is_visible(self, primitive):
		raise ValueError("Not implemented")

	def project(self, c):
		raise ValueError("Not implemented")