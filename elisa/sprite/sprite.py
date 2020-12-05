from __future__ import annotations
import os
import json
from uuid import uuid4
from pygame import Surface, PixelArray

from .sprites import load_image, load_png


# TODO: serialize the meta-data to json/dict struct, remove the internal id
# avoid to serialize the image data
class Sprite(object):
    def __init__(
        self, name: str, w: int, h: int, img, img_fp: str, z: int = 0, color_key=None
    ):
        """
        The Sprite is a pure data object holding limited property data about sprites, such as its underlying
        bit-mapped representation (image), its width or height. The PSprite object is a simplified version of
        pygame's Sprite that is required to make working with Sprite maps or texture catalogues easier.
        """
        super(Sprite, self).__init__()
        self._id = uuid4()
        self._name = name if name and name != "" else self._id
        self._width = w
        self._height = h
        self._image = img
        self._image_fp = img_fp
        self._z_order = z
        self._color_key = None
        self._visible = True

    @staticmethod
    def from_image(
        image_fp, name: str = None, color_key: tuple = None, verbose: bool = False
    ):
        if not image_fp or not os.path.exists(image_fp):
            raise ValueError("image path not valid")

        if verbose:
            print("Loading ... ", image_fp)
        p_image, rect = load_image(image_fp, colorkey=color_key, verbose=verbose)
        return Sprite(
            name,
            w=rect[2],
            h=rect[3],
            img=p_image,
            img_fp=image_fp,
            color_key=color_key,
        )

    @property
    def is_visible(self):
        return self._visible

    @is_visible.setter
    def is_visible(self, v: bool):
        if v is None:
            raise ValueError("v not provided")
        self._visible = v

    @property
    def color_key(self):
        return self._color_key

    @property
    def image_path(self):
        return self._image_fp

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if not name or name == "":
            raise ValueError("name not provided")
        self._name = name
        return self

    @property
    def z_order(self):
        return self._z_order

    @z_order.setter
    def z_order(self, z_order: int):
        self._z_order = z_order
        return self

    def to_json(self, filter_keys: list = ["_id", "_image"]) -> str:
        json_dict = [(k, v) for (k, v) in self.__dict__.items() if k not in filter_keys]
        return json.dumps(json_dict)

    @property
    def image(self) -> Surface:
        """
        Returns a pygame.Surface representing the sprite's underlying image.
        :return: pygame.Surface
        """
        return self._image

    @property
    def as_pygame_sprite(self):
        return self._image

    @property
    def pixel_array(self):
        return PixelArray(self._image)

    @property
    def width(self) -> int:
        """Returns the width in pixel of the sprite.

        Returns:
                        int: Width in pixel of the sprite
        """
        return self._width

    @property
    def height(self):
        """Returns the height in pixel of the sprite.

        Returns:
                        int: Height in pixel of the sprite
        """
        return self._height

    @property
    def image_rect(self):
        return self._image.get_rect()

    def __repr__(self):
        return "{} (w, h, z, vis, ckey => {}, {}, {}, {}, {})".format(
            self._id,
            self._width,
            self._height,
            self._z_order,
            "visible" if self._visible else "invisible",
            self._color_key if self._color_key else "No Color Key",
        )
