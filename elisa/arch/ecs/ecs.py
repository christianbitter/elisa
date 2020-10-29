from .core import ECSBase

class Message(ECSBase):
	"""Messages enable entities to interact.

	Args:
			ECSBase ([type]): [description]
	"""
	def __init__(self, msg_type):
		self._message_type = msg_type
		super(Message, self).__init__()

	@property
	def message_type(self):
		return self._message_type

	def __repr__(self):
	 return f"[Message/ {self._message_type}]: {self._id}"

	def __str__(self):
		return self.__repr__()

class System(ECSBase):
	"""Systems are responsible for interpreting entities and the components that are attached to them. Different systems for rendering,
	player input etc. can exist. Systems like components should be clearly delineated and handle single responsibilities.

	Args:
			ECSBase ([type]): [description]
	"""
	def __init__(self):
		super(System, self).__init__()

	def update(self, time_delta, entities):
		pass

	def send_msg(self, msg):
		pass

	def receive_msg(self, msg):
		pass
