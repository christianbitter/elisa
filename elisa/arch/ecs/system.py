import pygame
from .core import ECSBase


class System(ECSBase):
    """Systems are responsible for interpreting entities and the components that are attached to them. Different systems for rendering,
    player input etc. can exist. Systems like components should be clearly delineated and handle single responsibilities.
    Consider overriding the following methods:
        __init__
        update(self, time_delta, entities)
        send_msg(self, msg)
        receive_msg(self, msg)

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


class KeyboardInputSystem(System):
    """KeyboardInputSystem is a primitive implementation of a system reacting to keyboard input using Pygame keymap.
    It implements the update method querying for pygame.key.get_pressed(). If any key has been pressed the
    on_key_pressed handler function is invoked like so on_key_pressed(key_map, time_delta, entities)
    """

    def __init__(self):
        super(KeyboardInputSystem, self).__init__()

        self._on_key_pressed = None

    @property
    def on_key_pressed(self):
        return self._on_key_pressed

    @on_key_pressed.setter
    def on_key_pressed(self, fn):
        self._on_key_pressed = fn

    def update(self, time_delta: float, entities: list) -> None:
        """The systems update mechanism.

        Args:
                        time_delta (float): The time in milliseconds that passed since the last update call.
                        entities (list of entities): The entities present within our ecs managed world

        Returns:
                        None: None
        """
        if not entities or len(entities) < 1:
            return None

        key_map = pygame.key.get_pressed()

        if any(key_map):
            self._on_key_pressed(key_map, time_delta, entities)

    def send_msg(self, msg):
        return super().send_msg(msg)

    def receive_msg(self, msg):
        return super().receive_msg(msg)
