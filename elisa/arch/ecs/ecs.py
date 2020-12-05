from .core import ECSBase


class Message(ECSBase):
    """Messages enable entities to interact."""

    def __init__(self, msg_type):
        self._message_type = msg_type
        super(Message, self).__init__()

    @property
    def message_type(self) -> str:
        """Returns the message's type

        Returns:
                        str: the type name of the message
        """
        return self._message_type

    def __repr__(self):
        return f"[Message/ {self._message_type}]: {self._id}"

    def __str__(self):
        return self.__repr__()
