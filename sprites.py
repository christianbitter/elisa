import os
import pygame
import json
import uuid
from pygame import Surface, PixelArray

# TODO: support serialization for PSprite, etc.


def load_image(fp, colorkey=None, image_only: bool = False, verbose: bool = False):
    if not fp:
        raise ValueError("load_image - fp not provided")

    fullname = os.path.join(fp)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Cannot load image:", fp)
        raise SystemExit(message)

    if image.get_alpha() is None:
        if verbose:
            print("change the pixel format image to constant alpha or colorkey")
        image = image.convert()
    else:
        if verbose:
            print("change the pixel format image including per pixel alphas")
        image = image.convert_alpha()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        if verbose:
            print("Setting colour key: ", colorkey)
        image.set_colorkey(colorkey, pygame.RLEACCEL)

    if verbose:
        print("Loaded image: ", image)
    if image_only:
        return image
    else:
        return image, image.get_rect()


def load_png(fp, image_only=False):
    """ Load image and return image object"""
    if not fp:
        raise ValueError("load_png - fp not provided")
    if not os.path.exists(fp):
        raise ValueError("load_png - {} does not exist".format(fp))

    fullname = os.path.join(fp)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print("Cannot load image:", fullname)
        raise SystemExit(message)
    if image_only:
        return image
    else:
        return image, image.get_rect()


class PSprite(object):
    def __init__(self, s_id, w: int, h: int, img, z: int = 0):
        """
        The PSprite is a pure data object holding limited property data about sprites, such as its underlying
        bit-mapped representation (image), its width or height. The PSprite object is a simplified version of
        pygame's Sprite that is required to make working with Sprite maps or texture catalogues easier.
        """
        super(PSprite, self).__init__()
        self._id = s_id
        self._width = w
        self._height = h
        self._image = img
        self._z_order = z
        self._visible = True

    @staticmethod
    def from_image(image_fp, color_key: tuple = None, verbose: bool = False):
        if not image_fp or not os.path.exists(image_fp):
            raise ValueError("image path not valid")

        if verbose:
            print("Loading ... ", image_fp)
        p_image, rect = load_image(image_fp, colorkey=color_key, verbose=verbose)
        return PSprite(s_id=uuid.uuid4(), w=rect[2], h=rect[3], img=p_image)

    @property
    def is_visible(self):
        return self._visible

    @is_visible.setter
    def is_visible(self, v: bool):
        if v is None:
            raise ValueError("v not provided")
        self._visible = v

    @property
    def id(self):
        return self._id

    @property
    def z_order(self):
        return self._z_order

    @property
    def image(self) -> Surface:
        """
        Returns a pygame.Surface representing the sprite's underlying image.
        :return: pygame.Surface
        """
        return self._image

    @property
    def as_sprite(self):
        return self._image

    @property
    def as_pixel_array(self):
        return PixelArray(self._image)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def image_rect(self):
        return self._image.get_rect()

    def __repr__(self):
        return "{} (w, h => {}, {}, {}, {})".format(
            self._id, self._width, self._height, self._z_order, self._visible
        )


class SpriteMap(object):
    def __init__(self, json_descriptor: str):
        super(SpriteMap, self).__init__()
        self._descriptor = json_descriptor
        self._sprites = {}
        self._id = None
        self._description = None
        self._source = None
        self._image_path = None
        self._width = None
        self._height = None
        self._no_sprites = None
        self._sprites = {}
        self._initialized = False
        self._image = None
        self._sprites = {}
        self._idx2key = []
        self._sprite_names = []

    @property
    def initialized(self):
        return self._initialized

    def _load_image(self) -> None:
        img_name = os.path.basename(self._image_path)

        if img_name.endswith("png"):
            self._image, r = load_png(self._image_path)
        else:
            colour_key = None
            if self._color_key:
                colour_key = self._colour_key
            self._image, r = load_image(self._image_path, colour_key)

        self._width, self._height = r.width, r.height
        return None

    def initialize(self, verbose: bool = False):
        if not self._initialized:
            with open(self._descriptor, mode="r+") as fp:
                self._sprite_map = json.load(fp)

            if "id" not in self._sprite_map:
                raise ValueError("SpriteMap - id missing")
            if "width" not in self._sprite_map:
                raise ValueError("SpriteMap - width missing")
            if "height" not in self._sprite_map:
                raise ValueError("SpriteMap - height missing")
            if "image_path" not in self._sprite_map:
                raise ValueError("SpriteMap - image path missing")
            if "no_sprites" not in self._sprite_map:
                raise ValueError("SpriteMap - no_sprites missing")
            self._id = self._sprite_map["id"]
            self._width = self._sprite_map["width"]
            self._height = self._sprite_map["height"]
            self._image_path = self._sprite_map["image_path"]
            self._no_sprites = self._sprite_map["no_sprites"]
            self._colour_key = self._sprite_map["color_key"]

            self._description = self._sprite_map["description"]
            self._source = self._sprite_map["source"]

            self._load_image()
            # load sprites
            sprites = self._sprite_map["sprites"]
            for i, sprite_def in enumerate(sprites):
                id = sprite_def["id"]
                x = sprite_def["x"]
                y = sprite_def["y"]
                w = sprite_def["width"]
                h = sprite_def["height"]
                if verbose:
                    print(
                        "Loading subsurface:{}/ {}".format(
                            (x, y, w, h), (self._image.get_rect())
                        )
                    )
                sprite_img = self._image.subsurface(x, y, w, h)
                self._sprites[id] = PSprite(id, w, h, sprite_img)
                self._idx2key.append(id)

            if self._no_sprites > 0 and self._no_sprites != len(self._sprites):
                raise ValueError(
                    "Number of defined sprites does not match declared sprites"
                )

            self._sprite_names = [k for k, v in self._sprites.items()]
            self._initialized = True

    def __getitem__(self, item):
        if item is None:
            raise ValueError("SpriteMap.get - key not provided")

        if isinstance(item, int):
            return self._sprites[self._idx2key[item]]
        else:
            if item in self._sprites:
                return self._sprites[item]

        raise ValueError("SpriteMap.get - undefined sprite selected")

    @property
    def sprite_names(self):
        return self._sprite_names

    @property
    def no_sprites(self):
        return self._no_sprites

    def __len__(self):
        return self._no_sprites

    def __repr__(self):
        return "Sprite Map: {} # sprites {} -> {}".format(
            self._id, len(self._sprite_names), self._sprite_names
        )


class SpriteAssetManager(object):
    """
    The SpriteAssetManager is an abstraction over different sprite maps. That is, it allows us to conveniently
    register and access different sprites in sprite maps. It is simple in that you can only add or remove sprite maps.
    It allows index based access.
    """

    def __init__(self):
        """Constructor for AssetManager"""
        super(SpriteAssetManager, self).__init__()
        self._items = {}

    def __repr__(self):
        return "Registered Assets ({}): {}".format(len(self._items), self._items.keys())

    @property
    def number_of_sprite_maps(self):
        return len(self._items)

    def add_sprite_map(
        self,
        name: str,
        metadata_fp: str,
        initialize: bool = True,
        verbose: bool = False,
    ):
        if not name:
            raise ValueError("name not provided")
        if not metadata_fp:
            raise ValueError("metadata file not provided")
        if name in self._items:
            raise ValueError("asset already registered")
        if not os.path.exists(metadata_fp):
            raise ValueError("metadata file does not exist")

        if verbose:
            print("Adding Sprite Map: ", name)

        self._items[name] = SpriteMap(metadata_fp)
        if initialize:
            self._items[name].initialize(verbose=verbose)

        self._items[name] = SpriteMap(metadata_fp)
        if initialize:
            self._items[name].initialize()

    def remove_sprite_map(self, name):
        if not name:
            raise ValueError("name not provided")
        if name not in self._items:
            raise ValueError("asset not registered")
        del self._items[name]

    def get_sprite(self, sprite_map_name: str, sprite: str = None):
        if not sprite_map_name:
            raise ValueError("Asset cannot be none")
        if sprite_map_name not in self._items:
            raise ValueError("Unknown asset '{}'".format(sprite_map_name))
        sm = self._items[sprite_map_name]
        if not sprite:
            return sm
        if sprite not in sm:
            raise ValueError("Undefined sprite '{}' selected".format(sprite))
        return sm[sprite]

    def __getitem__(self, item):
        if item is None:
            raise ValueError("getitem - key not provided")

        if isinstance(item, int):
            return self._items[self._item_names[item]]
        else:
            if item in self._items:
                return self._items[item]

        raise ValueError("undefined sprite selected")

    def __len__(self):
        return len(self._items)

    def initialize(self, name: str = None, verbose: bool = False):
        if not name:
            for a in self._items:
                if not self._items[a].initialized:
                    a.initialize()
        else:
            if name not in self._items:
                raise ValueError("not an asset")
            if not self._items[name].initialized:
                self._items[name].initialize()
