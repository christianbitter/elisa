from __future__ import annotations

import os
import json
from uuid import uuid4
from .sprites import load_image, load_png
from .sprite import Sprite
from pygame import Surface, PixelArray
import xml.etree.ElementTree

# TODO: modification is only possible if not yet initialized
# TODO: serialize to json/dict struct, remove the internal id and persist to file
# TODO: add sprite (that does not exist) from the underlying image source
# TODO: remove sprite
# TODO: the color key is not currently used
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
			self._image, r = load_png(self._image_path, colorkey=self._color_key)
		else:
			self._image, r = load_image(self._image_path, self._color_key)

		self._width, self._height = r.width, r.height
		return None

	def initialize_from_spritemap(self, sprite_map:dict, **kwargs) -> SpriteSheet:
		"""Explicitly initializes the SpriteSheet using a dictionary of relevant fields. This allows to integrate other Sprite map sources.

		Args:
				sprite_map (dict): The dictionary used to initialize the internal SpriteSheet members

		Raises:
				ValueError: Raised when sprite_map is not presented or empty

		Returns:
				SpriteSheet: an initialized SpriteSheet
		"""
		if not sprite_map or len(sprite_map) == 0:
			raise ValueError("Sprite map cannot be null or empty")

		if not self._initialized:
			if 'name' not in sprite_map: 
				raise ValueError("SpriteMap - name missing")
			if 'width' not in sprite_map: 
				raise ValueError("SpriteMap - width missing")
			if 'height' not in sprite_map: 
				raise ValueError("SpriteMap - height missing")
			if 'image_path' not in sprite_map: 
				raise ValueError("SpriteMap - image path missing")
			if 'no_sprites' not in sprite_map: 
				raise ValueError("SpriteMap - no_sprites missing")

			verbose = kwargs.get("verbose", False)

			self._name = sprite_map['name']
			self._width = sprite_map['width']
			self._height = sprite_map['height']
			self._image_path = sprite_map['image_path']
			self._no_sprites = sprite_map['no_sprites']

			self._color_key = sprite_map['color_key']
			if not self._color_key or len(self._color_key) == 0 or self._color_key == {}:
				self._color_key = None

			self._description = sprite_map['description']
			self._source = sprite_map['source']

			if verbose:
				print("Color Key Defined?: ", self._color_key)

			self._load_image()
			# load sprites
			sprites = sprite_map['sprites']
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

				# if self._color_key:
				# 	if verbose:
				# 		print("Setting Color Key on surface")
				# 	sprite_img.set_colorkey(self._color_key)

				_sprite    = Sprite(_n, w, h, sprite_img, img_fp=self._image_path, color_key=self._color_key)

				self._sprites[_sprite.id] = _sprite
				self._name2id[_n] = _sprite.id

			if self._no_sprites > 0 and self._no_sprites != len(self._sprites):
				raise ValueError("Number of defined sprites does not match declared sprites")
			
			self._initialized = True
		return self

	def initialize(self, **kwargs) -> SpriteSheet:
		"""If not already initialized, the SpriteSheet is initialized by loading the descriptor file.
		That is, all indiviudal sprites are loaded into separate Sprite objects and indexed in the SpriteSheets members.

		Returns:
				SpriteSheet: Initialized SpriteSheet (e.g., initialized property set to true).
		"""
		if not self._initialized:
			with open(self._descriptor, mode='r+') as fp:
				_sprite_map = json.load(fp)
				return self.initialize_from_spritemap(_sprite_map, **kwargs)

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
	def sprite_names(self) -> string:
		"""Returns the names of sprites defined in the SpriteSheet

		Returns:
				string: name of individual sprites
		"""
		return set(self._name2id.keys())

	@property
	def no_sprites(self) -> int:
		"""Returns the number of sprites represented by this SpriteSheet

		Returns:
				int: number of Sprites
		"""
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
		"""Creates and initializes a SpriteSheet from a JSON descriptor

		Args:
				json_descriptor_fp (str): The metadata descriptor file holding the relevant SpriteSheet reference information.

		Raises:
				ValueError: Raised if the descriptor does not exist, is not provided, is empty or relevant data members are not defined
										in that descriptor.

		Returns:
				SpriteSheet: An initialized SpriteSheet. Note: pygame.display needs to be initialized for loading the sprite surfaces.
		"""
		if not json_descriptor_fp or json_descriptor_fp.strip() == '':
			raise ValueError("json descriptor not provided")
		if not os.path.exists(json_descriptor_fp):
			raise ValueError("Json descriptor does not exist")

		verbose = kwargs.get('verbose', False)

		_sheet = SpriteSheet(json_descriptor_fp)
		_sheet.initialize(verbose=verbose)
		return _sheet


def spritesheet_from_tiled(tsx_fp:str, **kwargs):
	if not tsx_fp or tsx_fp.strip() == '':
		raise ValueError("tsx_fp cannot be empty")
	if not os.path.exists(tsx_fp):
		raise ValueError("tsx file does not exist")
	if tsx_fp.endswith(".tsx") == False:
		raise ValueError("tsx_fp does not end in tsx")

	root = xml.etree.ElementTree.parse(tsx_fp).getroot()
	tsx_dir_fp = os.path.dirname(tsx_fp)

	# version="1.4" tiledversion="1.4.2" name="test_tiled_tileset" tilewidth="64" tileheight="64" tilecount="5" columns="5"
	tiledVersion = root.attrib["tiledversion"]
	name = root.attrib["name"]
	tilewidth = int(root.attrib["tilewidth"])
	tileheight = int(root.attrib["tileheight"])
	tilecount = int(root.attrib["tilecount"])
	columns = int(root.attrib["columns"])
	spacing = int(root.attrib.get("spacing", 0))
	margin = int(root.attrib.get("margin", 0))

	l = len(root)
	if len(root) > 1:
		raise ValueError("Only single sprite sheet tilesets currently supported")
	atlas_def = root.find("image")
	
	# output multiple tile atlasses per def		
	image_source = os.path.join(tsx_dir_fp, atlas_def.attrib["source"])
	image_width  = int(atlas_def.attrib["width"])
	color_key    = atlas_def.attrib.get("trans", None)
	image_height = int(atlas_def.attrib["height"])

	# if a color key is defined it needs to be converted to an RGBA triplet
	if color_key:
		# TODO: parse the triplet from the key
		color_triplet = (255, 255, 255)
		color_key = color_triplet

	sprites = []

	# spacing: The spacing in pixels between the tiles in this tileset (applies to the tileset image, defaults to 0)
	# margin: The margin around the tiles in this tileset (applies to the tileset image, defaults to 0)
	# add the margin to x start, y start
	# add the spacing between images
	# the color key applies to the sheet
	_ix = 0
	_iy = 0
	_x, _y = margin, margin
	for j in range(tilecount):
		# next horizontal layer - we reset x and increment y
		sprites.append({
			"name": f"{name}_{j}",
			"x": _x,
			"y": _y,
			"width": tilewidth,
			"height": tileheight
		})

		# move to the next image in the horizontal layer by adding ... tile_width, margin, spacing, margin
		_x = _x + tilewidth + margin + spacing + margin

		if (j + 1) % columns == 0:
			_iy += 1
			_ix = 0
			_x  = margin
			_y  = _y + tileheight + margin + spacing + margin


	tileset_desc_json = {
		"name": name if l == 1 else f"{name}_{i}".format(i),
		"description": "Autogenerated tile set descriptor from Tiled",
		"source": "Tiled",
		"image_path": image_source,
		"width": image_width,
		"height": image_height,
		"no_sprites": tilecount,
		"color_key": color_key if color_key else None,
		"sprites": sprites
	}

	return SpriteSheet(json_descriptor=tsx_fp).initialize_from_spritemap(tileset_desc_json, **kwargs)

class TextureAtlas(SpriteSheet):
	def __init__(self, descriptor_fp):
		super(TextureAtlas, self).__init__(descriptor_fp)