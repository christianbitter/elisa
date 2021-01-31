from __future__ import annotations

from elisa.arch.ecs import ECSBase


class Scene(ECSBase):
    """A scene binds together different entities with different components that can be
    processed by different systems. Attached to a scene is a camera.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._entity_registry = {}
        self._component_registry = {}
        self._system_registry = {}
        # TODO: set up default camera
        self._camera = None

    def __repr__(self) -> str:
        return "Scene[{}]".format(self.id)

    def __str__(self) -> str:
        return self.__repr__()
