from __future__ import annotations
import os
from .spritesheet import SpriteSheet


# TODO: create image index across different sprite sheets ... names may clash
class SpriteAssetManager(object):
    """
    The SpriteAssetManager is an abstraction over different sprite maps. That is, it allows us to conveniently
    register and access different sprites in sprite maps. It is simple in that you can only add or remove sprite maps.
    It allows index based access.
    """

    def __init__(self):
        """Constructor for AssetManager"""
        super(SpriteAssetManager, self).__init__()
        self._sheets = {}
        self._sprites = {}

    def __repr__(self):
        return "Registered Assets ({}): {}".format(len(self._items), self._items.keys())

    @property
    def number_of_sprite_maps(self):
        return len(self._items)

    def add_sprite_sheet(
        self,
        sheet: SpriteSheet = None,
        name: str = None,
        metadata_fp: str = None,
        initialize: bool = True,
        verbose: bool = False,
    ):
        """Add a Sprite Sheet to the Manager either directly, i.e. the SpriteSheet instance or register from an underlying descriptor.

        Args:
            sheet (SpriteSheet, optional): [description]. Defaults to None.
            name (str, optional): [description]. Defaults to None.
            metadata_fp (str, optional): [description]. Defaults to None.
            initialize (bool, optional): [description]. Defaults to True.
            verbose (bool, optional): [description]. Defaults to False.

        Raises:
            ValueError: An exception is raised if no SpriteSheet instance is provided and/ or no name, a duplicate name, no descriptor, or no valid descriptor are given.

        Returns:
            SpriteSheet: The added SpriteSheet
        """
        _sheet = None
        if not sheet:
            if not name:
                raise ValueError("name not provided")
            if not metadata_fp:
                raise ValueError("metadata file not provided")
            if name in self._items:
                raise ValueError("asset already registered")
            if not os.path.exists(metadata_fp):
                raise ValueError("metadata file does not exist")

            if verbose:
                print("Adding Sprite Sheet: ", name)

            _sheet = SpriteSheet(metadata_fp)
        elif sheet:
            _sheet = sheet
        else:
            raise ValueError(
                "Neither SpriteSheet instance nor descriptor provided to register a new SpriteSheet"
            )

        self._sheets[_sheet.id] = _sheet
        if initialize:
            self.initialize(name=_sheet.id, verbose=verbose)

        return _sheet

    def remove_sprite_sheet(self, name):
        if not name:
            raise ValueError("name not provided")
        if name not in self._items:
            raise ValueError("asset not registered")
        del self._items[name]

    def get_sprite(self, sprite_sheet_name: str, sprite: str = None):
        if not sprite_sheet_name:
            raise ValueError("Asset cannot be none")
        if sprite_sheet_name not in self._items:
            raise ValueError("Unknown asset '{}'".format(sprite_sheet_name))
        sm = self._items[sprite_sheet_name]
        if not sprite:
            return sm
        if sprite not in sm:
            raise ValueError("Undefined sprite '{}' selected".format(sprite))
        return sm[sprite]

    def __getitem__(self, item):
        if item is None:
            raise ValueError("getitem - key not provided")
        if isinstance(item, int):
            _item_names = self._sheets.keys()
            return self._sheets[_item_names[item]]
        else:
            if item in self._sheets:
                return self._sheets[item]

        raise ValueError("undefined sprite selected")

    def __len__(self):
        return len(self._items)

    def _add_images_to_index(self, sheet: str):
        pass

    def initialize(self, name: str = None, verbose: bool = False):
        if name and name not in self._sheets:
            raise ValueError("Spritesheet not registered")

        names = set(self._sheets.keys()) if not name else [name]
        for a in names:
            if not self._sheets[a].initialized:
                a.initialize()

        return self
