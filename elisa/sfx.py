from __future__ import annotations

import os
from queue import Queue

import pygame.mixer
from arch.ecs import ECSBase, ECSManager


class SFX(ECSBase):
    def __init__(self, path_fp: str, **kwargs):
        super().__init__(**kwargs)
        self._path_fp = path_fp
        self._sound = pygame.mixer.Sound(path_fp)

    @property
    def as_pygame_sound(self) -> pygame.mixer.Sound:
        return self._sound

    def __len__(self) -> float:
        return self._sound.get_length()

    @property
    def raw_bytes(self) -> bytes:
        return self._sound.get_raw()


class SFXManager(ECSManager):
    def __init__(self):
        super(SFXManager, self).__init__()
        self._unloaded_assets = []

    def register(self, asset_fp: str) -> SFXManager:
        if asset_fp is None or asset_fp.strip() == "":
            raise ValueError("sfx asset path not provided")
        if os.path.exists(asset_fp) is False:
            raise ValueError("asset does not exist under the provided path")

        super().register(asset_fp)

        # put the asset into the queue of known assets
        if asset_fp not in self._unloaded_assets:
            self._unloaded_assets.append(asset_fp)

        return self

    def acquire(self, asset_fp: str = None):
        if asset_fp is None:
            while len(self._unloaded_assets) > 0:
                _ua = self._unloaded_assets[0]
                _sfx = SFX(_ua)
                self._o_map[_sfx.id] = _sfx
                if self._on_asset_acquired:
                    self._on_asset_acquired(_sfx)
                self._unloaded_assets.remove(_ua)
        else:
            if asset_fp.strip() == "":
                raise AttributeError("asset not provided")

            if asset_fp not in self._unloaded_assets:
                raise AttributeError("asset not registered")

            _uai = self._unloaded_assets.index(asset_fp)
            _ua = self._unloaded_assets[_uai]
            _sfx = SFX(_ua)
            self._o_map[_sfx.id] = _sfx
            if self._on_asset_acquired:
                self._on_asset_acquired(_sfx)
            self._unloaded_assets.remove(_ua)
