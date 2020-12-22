from __future__ import annotations

from elisa.arch.ecs.core import ECSBase


class Message(ECSBase):
    """Messages enable entities to interact."""

    def __init__(self, msg_type: str, sender=None, receiver=None, **kwargs):
        super(Message, self).__init__(**kwargs)
        self._message_type = msg_type
        self._sender = sender
        self._receiver = receiver

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

    @classmethod
    def direct(cls, msg_type: str, sender, receiver, **kwargs) -> Message:
        if not msg_type or msg_type.strip() == "":
            raise ValueError("No message type provided")
        return cls(msg_type=msg_type, sender=sender, receiver=receiver, **kwargs)

    @classmethod
    def broadcast(cls, msg_type: str, sender, receiver: list, **kwargs) -> list:
        if not msg_type or msg_type.strip() == "":
            raise ValueError("No message type provided")
        if not receiver or len(receiver) < 1:
            raise ValueError("No recepient defined for broadcast")
        return [
            cls(msg_type=msg_type, sender=sender, receiver=r, **kwargs)
            for r in receiver
        ]


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
