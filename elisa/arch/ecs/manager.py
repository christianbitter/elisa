from __future__ import annotations

from .core import ECSBase


# We start with a simple manager like entity, i.e. it does not encapsulate creation/ factory
# TODO: finalize
# TODO: adapt to asset management like graphics, and audio
# TODO: make this a singleton
# https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html?highlight=singleton
class ECSManager(ECSBase):
    """A manager is an entity that is responsible for resource loading, including assets like graphics or sound effects.
    The manager follows an operation model whereby assets are:
    - first registered, this makes them known to the managing entity
    - loaded or acquired, i.e. this loads the asset into the memory space managed by the entity manager
    - requested, i.e. delivered to the consumer
    """

    def __init__(self, **kwargs):
        super(ECSManager, self).__init__(**kwargs)
        self._o_map = {}
        self._on_asset_acquired = None
        self._on_asset_released = None

    def register(self, asset_descriptor) -> ECSManager:
        pass

    def request(self, resource_id: str):
        raise ValueError("Not implemented")

    def acquire(self, asset_descriptor: list = None):
        raise ValueError("Not implemented")

    def release(self, resource_ids: list = None):
        raise ValueError("Not implemented")

    @property
    def on_asset_acquired(self):
        return self._on_asset_acquired

    @on_asset_acquired.setter
    def on_asset_acquired(self, v) -> ECSManager:
        self._on_asset_acquired = v
        return self

    @property
    def on_asset_released(self):
        return self._on_asset_released

    @on_asset_released.setter
    def on_asset_released(self, v) -> ECSManager:
        self._on_asset_released = v
        return self
