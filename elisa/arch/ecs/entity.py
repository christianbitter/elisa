from __future__ import annotations

from .core import ECSBase
from .component import Component
from .ecs import Message
from uuid import uuid4, UUID


# TODO: we need to allow for multiple components of the same type
# TODO: components need to indicate if they can be registered multiple times on the same entity


class Entity(ECSBase):
    """An entity is a named collection of components. You can add, remove, or search for components that the entity has registered. Additionally,
    entities can send messages to other entities and receive messages from other objects.

    Consider overriding the following method:
        - send_msg(self, msg)
    """

    def __init__(self, **kwargs):
        """Creates a new entity instance."""
        super(Entity, self).__init__(**kwargs)
        self._components = dict()
        self._ctypes = dict()

    def add(self, c: Component):
        """Add a component to an entity. Only one component per type is allowed on an entity.

        Args:
                        c (Component): Component to register

        Raises:
                        ValueError: if the component is not provided/ is None
                        ValueError: if the component has been registered before

        Returns:
                        [Entity]: the entity
        """
        if not c:
            raise ValueError("No component provided")
        cid = str(c._id)
        if cid in self._components:
            raise ValueError("Component already exists")

        ctype = c._component_type
        self._components[str(c._id)] = c
        if ctype not in self._ctypes:
            self._ctypes[ctype] = []

        self._ctypes[ctype].append(cid)

        return self

    def __setitem__(self, key, value: Component):
        if not key:
            raise ValueError("key not provided")

        if not (isinstance(key, UUID) or isinstance(key, str)):
            raise ValueError("key must be uuid string or uuid")

        temp_uuid = key
        if isinstance(key, str):
            temp_uuid = UUID(key)

        if temp_uuid != value.id:
            raise ValueError("cannot register component under different uuid")

        self.add(value)

    def __getitem__(self, key):
        if isinstance(key, int):
            if key > len(self._components):
                raise ValueError("index outside of registered components")
            for i, k in enumerate(self._components):
                if i == key:
                    return self._components[k]
        else:
            key = str(key)
            return self._components[key]

    def get_of_type(self, component_type: str):
        """Get the first component of a specific type associated with the entity.

        Args:
                        component_type (str): type of the component, you wish to retrieve

        Raises:
                        ValueError: if the component type is not provided, or is not found among the entities components.

        Returns:
                        Component or list of component: if only a single instance is registered of the supplied type, then the individual instance is returned. Else
                        a list of component instances is returned.
        """
        if not component_type:
            raise ValueError("component_type not provided")
        if len(self._components) < 1:
            raise ValueError("entity does not have any associated component")

        ci = self._ctypes[component_type]
        if len(ci) == 1:
            return self._components[ci[0]]
        else:
            return [self._components[cid] for cid in ci]

    def has_component_type(self, component_type) -> bool:
        """Interrogates the underlying entity about the presence of a component of a specific type. In the case of a single type query,
        the entity is checked for the presence and a True/False result is delivered. If a list of type names is passed, all component
        types have to be defined on the entity for a True result.

        Args:
                        component_type (str or list of str): the component type name to query the entity for.

        Raises:
                        ValueError: if component type is none, an empty list or the empty string

        Returns:
                        bool: result of the type query
        """
        if not component_type or component_type == "":
            raise ValueError("component_type not provided")

        if isinstance(component_type, str):
            return component_type in self._ctypes
        elif isinstance(component_type, list):
            if len(component_type) < 1:
                raise ValueError("component_type cannot be an empty list")

            _types = [(t in self._ctypes) for t in component_type]
            return all(_types)
        else:
            raise ValueError(
                "component type has to be a list of strings or an individual string"
            )

    def remove(self, component_id: str):
        if not component_id or component_id == "":
            raise ValueError("No component id provided")

        if component_id in self._components:
            ctype = self._components[component_id]._component_type

            self._ctypes[ctype].remove(component_id)
            if len(self._ctypes[ctype]) < 1:
                delattr(self._ctypes, ctype)

        # support chaining
        return self

    def send_msg(self, msg: Message):
        pass

    def __repr__(self) -> str:
        c_str = f"Entity: {self._id}/ {type(self).__name__}\r\n"
        if len(self._components) == 0:
            c_str += "No registered components"
        else:
            for i, k in enumerate(self._components):
                c_str += "[+{}] = {}\r\n".format(i, self._components[k])
        return c_str

    def __str__(self) -> str:
        return self.__repr__()
