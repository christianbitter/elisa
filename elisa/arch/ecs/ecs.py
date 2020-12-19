from .core import ECSBase


class Message(ECSBase):
    """Messages enable entities to interact."""

    def __init__(self, msg_type, **kwargs):
        super(Message, self).__init__(**kwargs)
        self._message_type = msg_type

    @property
    def message_type(self) -> str:
        """Returns the message's type

        Returns:
                        str: the type name of the message
        """
        return self._message_type

    def __repr__(self) -> str:
        return f"[Message/ {self._message_type}]: {self._id}"

    def __str__(self) -> str:
        return self.__repr__()


class ClockMessage(Message):
    def __init__(self, time_delta_ms: float, **kwargs):
        super(ClockMessage, self).__init__("Clock", **kwargs)
        self._elapsed_time_ms = time_delta_ms

    @property
    def elapsed_time_ms(self) -> float:
        return self._elapsed_time_ms

    def __repr__(self) -> str:
        return f"[Message/{self._message_type} ({self._id})]: {self.elapsed_time_ms}"

    def __str__(self) -> str:
        return self.__repr__()
