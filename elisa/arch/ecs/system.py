from __future__ import annotations

import pygame

from . import ECSBase


class System(ECSBase):
    """Systems are responsible for interpreting entities and the components that are attached to them. Different systems for rendering,
    player input etc. can exist. Systems like components should be clearly delineated and handle single responsibilities.
    Consider overriding the following methods:
        __init__
        update(self, time_delta, entities)
        initialize(self, **kwargs)
        finalize(self, **kwargs)
        send_msg(self, msg)
        receive_msg(self, msg)
    """

    def __init__(self, **kwargs):
        """Creates a new system instance."""
        super(System, self).__init__(**kwargs)

    def update(self, time_delta: float, entities):
        """Advance the state of the system

        Args:
            time_delta (float): time passed between last invocation of the method and now.
            entities ([type]): entities to update.
        """
        pass

    def initialize(self, **kwargs):
        """Initialize the system."""
        pass

    def finalize(self, **kwargs):
        """Shut the system down"""
        pass

    def send_msg(self, msg):
        pass

    def receive_msg(self, msg):
        pass

    def __repr__(self) -> str:
        return "System[{}]".format(self.id)

    def __str__(self) -> str:
        return self.__repr__()


class KeyboardInputSystem(System):
    """KeyboardInputSystem is a primitive implementation of a system reacting to keyboard input using Pygame keymap.
    It implements the update method querying for pygame.key.get_pressed(). If any key has been pressed the
    on_key_pressed handler function is invoked like so on_key_pressed(key_map, time_delta, entities)
    """

    def __init__(self, **kwargs):
        super(KeyboardInputSystem, self).__init__(**kwargs)
        self._on_key_pressed = None
        self._on_key_released = None
        self._keymap = pygame.key.get_pressed()
        self._keymap_released = {
            pygame.K_BACKSPACE: False,
            pygame.K_TAB: False,
            pygame.K_CLEAR: False,
            pygame.K_RETURN: False,
            pygame.K_PAUSE: False,
            pygame.K_ESCAPE: False,
            pygame.K_SPACE: False,
            pygame.K_EXCLAIM: False,
            pygame.K_QUOTEDBL: False,
            pygame.K_HASH: False,
            pygame.K_DOLLAR: False,
            pygame.K_AMPERSAND: False,
            pygame.K_QUOTE: False,
            pygame.K_LEFTPAREN: False,
            pygame.K_RIGHTPAREN: False,
            pygame.K_ASTERISK: False,
            pygame.K_PLUS: False,
            pygame.K_COMMA: False,
            pygame.K_MINUS: False,
            pygame.K_PERIOD: False,
            pygame.K_SLASH: False,
            pygame.K_0: False,
            pygame.K_1: False,
            pygame.K_2: False,
            pygame.K_3: False,
            pygame.K_4: False,
            pygame.K_5: False,
            pygame.K_6: False,
            pygame.K_7: False,
            pygame.K_8: False,
            pygame.K_9: False,
            pygame.K_COLON: False,
            pygame.K_SEMICOLON: False,
            pygame.K_LESS: False,
            pygame.K_EQUALS: False,
            pygame.K_GREATER: False,
            pygame.K_QUESTION: False,
            pygame.K_AT: False,
            pygame.K_LEFTBRACKET: False,
            pygame.K_BACKSLASH: False,
            pygame.K_RIGHTBRACKET: False,
            pygame.K_CARET: False,
            pygame.K_UNDERSCORE: False,
            pygame.K_BACKQUOTE: False,
            pygame.K_a: False,
            pygame.K_b: False,
            pygame.K_c: False,
            pygame.K_d: False,
            pygame.K_e: False,
            pygame.K_f: False,
            pygame.K_g: False,
            pygame.K_h: False,
            pygame.K_i: False,
            pygame.K_j: False,
            pygame.K_k: False,
            pygame.K_l: False,
            pygame.K_m: False,
            pygame.K_n: False,
            pygame.K_o: False,
            pygame.K_p: False,
            pygame.K_q: False,
            pygame.K_r: False,
            pygame.K_s: False,
            pygame.K_t: False,
            pygame.K_u: False,
            pygame.K_v: False,
            pygame.K_w: False,
            pygame.K_x: False,
            pygame.K_y: False,
            pygame.K_z: False,
            pygame.K_DELETE: False,
            pygame.K_KP0: False,
            pygame.K_KP1: False,
            pygame.K_KP2: False,
            pygame.K_KP3: False,
            pygame.K_KP4: False,
            pygame.K_KP5: False,
            pygame.K_KP6: False,
            pygame.K_KP7: False,
            pygame.K_KP8: False,
            pygame.K_KP9: False,
            pygame.K_KP_PERIOD: False,
            pygame.K_KP_DIVIDE: False,
            pygame.K_KP_MULTIPLY: False,
            pygame.K_KP_MINUS: False,
            pygame.K_KP_PLUS: False,
            pygame.K_KP_ENTER: False,
            pygame.K_KP_EQUALS: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_RIGHT: False,
            pygame.K_LEFT: False,
            pygame.K_INSERT: False,
            pygame.K_HOME: False,
            pygame.K_END: False,
            pygame.K_PAGEUP: False,
            pygame.K_PAGEDOWN: False,
            pygame.K_F1: False,
            pygame.K_F2: False,
            pygame.K_F3: False,
            pygame.K_F4: False,
            pygame.K_F5: False,
            pygame.K_F6: False,
            pygame.K_F7: False,
            pygame.K_F8: False,
            pygame.K_F9: False,
            pygame.K_F10: False,
            pygame.K_F11: False,
            pygame.K_F12: False,
            pygame.K_F13: False,
            pygame.K_F14: False,
            pygame.K_F15: False,
            pygame.K_NUMLOCK: False,
            pygame.K_CAPSLOCK: False,
            pygame.K_SCROLLOCK: False,
            pygame.K_RSHIFT: False,
            pygame.K_LSHIFT: False,
            pygame.K_RCTRL: False,
            pygame.K_LCTRL: False,
            pygame.K_RALT: False,
            pygame.K_LALT: False,
            pygame.K_RMETA: False,
            pygame.K_LMETA: False,
            pygame.K_LSUPER: False,
            pygame.K_RSUPER: False,
            pygame.K_MODE: False,
            pygame.K_HELP: False,
            pygame.K_PRINT: False,
            pygame.K_SYSREQ: False,
            pygame.K_BREAK: False,
            pygame.K_MENU: False,
            pygame.K_POWER: False,
            pygame.K_EURO: False,
        }

    @property
    def on_key_pressed(self):
        return self._on_key_pressed

    @property
    def on_key_released(self):
        return self._on_key_released

    @on_key_pressed.setter
    def on_key_pressed(self, fn) -> KeyboardInputSystem:
        self._on_key_pressed = fn
        return self

    @on_key_released.setter
    def on_key_released(self, fn) -> KeyboardInputSystem:
        self._on_key_released = fn
        return self

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

        pressed = pygame.key.get_pressed()
        self.update_released_state(pressed)
        self._keymap = pressed

        _to_update = [
            (e, e.get_of_type(component_type="HandlesKBInput"))
            for e in entities
            if e.has_component_type(component_type="HandlesKBInput")
        ]

        if len(_to_update) < 1:
            return None

        if self._on_key_pressed is not None and any(pressed):
            self._on_key_pressed(pressed, time_delta, entities)

        if self._on_key_released is not None:
            self._on_key_released(self._keymap_released, time_delta, entities)

        for e, ec in _to_update:
            if ec.on_key_pressed:
                ec.on_key_pressed(pressed, time_delta)
            if ec.on_key_released:
                ec.on_key_released(self._keymap_released, time_delta)

    def update_released_state(self, new_pressed_map) -> None:
        if new_pressed_map is None:
            raise ValueError("Key Map not provided")

        for k in self._keymap_released:
            # if it was pressed before and now not anymore, then it was released
            self._keymap_released[k] = self._keymap[k] and not new_pressed_map[k]

    def send_msg(self, msg):
        return super().send_msg(msg)

    def receive_msg(self, msg):
        return super().receive_msg(msg)
