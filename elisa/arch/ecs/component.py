from __future__ import annotations

from .core import ECSBase


class Component(ECSBase):
    """The Component in the ECS decomposition approach. The Component is derived from ECS base, and for that matter has assigned an internal id.
    the allow_multiple_on_entity should indicate if an entity can have multiple components of the respective type.
    However, this is not enforced at the component level but needs to be ensured by the entity or some outside entity.
    """

    allow_multiple_on_entity = True

    """A component is simply a collection of state that defines an entity in the game world. Components can bind properties
    like position, velocity or health.
    Args:
            ECSBase ([type]): [description]
    """

    def __init__(self, component_type):
        super(Component, self).__init__()
        self._component_type = component_type

    @property
    def component_type(self) -> str:
        return self._component_type

    def __repr__(self) -> str:
        return f"[Component/ {self._component_type}]: {self._id}"

    def __str__(self) -> str:
        return self.__repr__()

    def update(self, time_delta):
        pass

    def serialize(self) -> str:
        # TODO: component serialize
        return super().serialize()

    def deserialize(self, str_rep) -> Component:
        # TODO: component deserialize
        return super().deserialize(str_rep)


class HandlesKBInputComponent(Component):
    def __init__(self, registered_keys: list):
        super(HandlesKBInputComponent, self).__init__("HandlesKBInput")
        self._registered_keys = registered_keys
        self._on_key_pressed = None
        self._on_key_released = None

    @property
    def registered_keys(self) -> list:
        return self._registered_keys

    def is_registered(self, key) -> bool:
        if not key:
            raise ValueError("key not provided")
        return key in self._registered_keys

    @property
    def on_key_pressed(self):
        return self._on_key_pressed

    @property
    def on_key_released(self):
        return self._on_key_released

    @on_key_pressed.setter
    def on_key_pressed(self, v) -> HandlesKBInputComponent:
        self._on_key_pressed = v
        return self

    @on_key_released.setter
    def on_key_released(self, v) -> HandlesKBInputComponent:
        self._on_key_released = v
        return self
