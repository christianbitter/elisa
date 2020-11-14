from __future__ import annotations

import os
import json
from uuid import uuid4
from .sprites import load_image, load_png
from .sprite import Sprite
from pygame import Surface, PixelArray

# TODO: modification is only possible if not yet initialized
# TODO: serialize to json/dict struct, remove the internal id and persist to file
# TODO: add sprite (that does not exist) from the underlying image source
# TODO: remove sprite
class SpriteSheet(object):
	"""A collection of Sprite objects defined within the same underlying image data source.
	"""
	def __init__(self, json_descriptor: str):
		super(SpriteSheet, self).__init__()
		self._descriptor = json_descriptor
		self._sprites = {}
		self._id = uuid4()
		self._name = None
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
		self._name2id = {}

	@property
	def number_of_sprites(self):
		return self._no_sprites

	@property
	def name(self):
		return self._name
	
	@property
	def description(self):
		return self._description

	@description.setter
	def description(self, v):
		self._description = v
		return self

	@property
	def source(self):
		return self._source
	
	@property
	def image_path(self):
		return self._image_path

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
			with open(self._descriptor, mode='r+') as fp:
				self._sprite_map = json.load(fp)

			if 'name' not in self._sprite_map: 
				raise ValueError("SpriteMap - name missing")
			if 'width' not in self._sprite_map: 
				raise ValueError("SpriteMap - width missing")
			if 'height' not in self._sprite_map: 
				raise ValueError("SpriteMap - height missing")
			if 'image_path' not in self._sprite_map: 
				raise ValueError("SpriteMap - image path missing")
			if 'no_sprites' not in self._sprite_map: 
				raise ValueError("SpriteMap - no_sprites missing")

			self._name = self._sprite_map['name']
			self._width = self._sprite_map['width']
			self._height = self._sprite_map['height']
			self._image_path = self._sprite_map['image_path']
			self._no_sprites = self._sprite_map['no_sprites']
			self._colour_key = self._sprite_map['color_key']

			self._description = self._sprite_map['description']
			self._source = self._sprite_map['source']

			self._load_image()
			# load sprites
			sprites = self._sprite_map['sprites']
			if verbose:
				print("Source Image Surface: {}".format(self._image.get_rect()))
				
			for i, sprite_def in enumerate(sprites):
				_n = sprite_def['name']
				x = sprite_def['x']
				y = sprite_def['y']
				w = sprite_def['width']
				h = sprite_def['height']
				if _n in self._name2id:
					raise ValueError("Sprite already registered with that name")

				if verbose:
					print("Loading subsurface:{}".format((x, y, w, h)))
				sprite_img = self._image.subsurface(x, y, w, h)
				_sprite    = Sprite(_n, w, h, sprite_img, img_fp=self._image_path)

				self._sprites[_sprite.id] = _sprite
				self._name2id[_n] = _sprite.id

			if self._no_sprites > 0 and self._no_sprites != len(self._sprites):
				raise ValueError("Number of defined sprites does not match declared sprites")
			
			self._initialized = True

	def __getitem__(self, item) -> Sprite:
		"""Returns a sprite from the sprite sheet by using the Sprite's name (preference) or the index in the sprite map.

		Args:
				item (string or int): name of the sprite as defined in the sprite sheets metadata descriptor, or the index in the sprite sheet.

		Raises:
				ValueError: if the key is not provided or the sprite could not be retrieved

		Returns:
				Sprite: the underlying pygame Sprite instance
		"""
		if item is None:
			raise ValueError("SpriteMap.get - key not provided")

		if isinstance(item, int):
			return self._sprites[self._idx2key[item]]
		else:
			if item in self._sprites:
				return self._sprites[item]
			if item in self._name2id:
				return self._sprites[self._name2id[item]]

		raise ValueError("SpriteMap.get - undefined sprite selected")

	@property
	def sprite_names(self):
		return set(self._name2id.keys())

	@property
	def no_sprites(self):
		return self._no_sprites

	def __len__(self):
		return self._no_sprites

	def __repr__(self):
		_sn = self.sprite_names
		return "Sprite Map: {} # sprites {} -> {}".format(self._id, len(_sn), _sn)

	@property
	def image(self) -> Surface:
		"""
		Returns a pygame.Surface representing the sprite's underlying image.
		:return: pygame.Surface
		"""
		return self._image

	@property
	def pixel_array(self):
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

	@staticmethod
	def create(json_descriptor_fp:str, **kwargs) -> SpriteSheet:
		if not json_descriptor_fp or json_descriptor_fp.strip() == '':
			raise ValueError("json descriptor not provided")
		if not os.path.exists(json_descriptor_fp):
			raise ValueError("Json descriptor does not exist")

		verbose = kwargs.get('verbose', False)

		_sheet = SpriteSheet(json_descriptor_fp)
		_sheet.initialize(verbose=verbose)
		return _sheet

class TextureAtlas(SpriteSheet):
	def __init__(self):
		super(TileAtlas, self).__init__()