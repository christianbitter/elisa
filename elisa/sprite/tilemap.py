from __future__ import annotations
from .sprite import Sprite
from .spritesheet import SpriteSheet
from uuid import uuid4

# a Tile is the binding element between the index in the grid structure
# and the system defining meaning for it, such as a sprite sheet or a logical system that defines a logical tile
class Tile(object):
	def __init__(self):
		super(Tile, self).__init__()
		self._id = uuid4()

# for starters we closely follow: https://developer.mozilla.org/en-US/docs/Games/Techniques/Tilemaps
# Initially we start with a single tile atlas
# but
# TODO: 1 to many tile atlas - this serves as our repository of visual tiles
# an index from the tile atlas tile to the visual grid needs to be established
# TODO: set tile at coords for the visual and the logical tile

# TODO: should we simplify the grids into one structure, and defining an abstract grid type (visual, logical)
class TileMap(object):
	"""A 2D Tile Map Structure
	"""
	def __init__(self, tile_extent: int, map_width: int, map_height: int):
		"""Creates a new 2D tile map structure

		Args:
				tile_extent (int): square length of tile in px (e.g., 8 pixel)
				map_width (int): map width in terms of tiles
				map_height (int): map height in terms of tiles

		Raises:
				ValueError: raises an exception if the tile extent is not positive or the map extent is not positive.
		"""
		super(TileMap, self).__init__()

		if not tile_extent:
			raise ValueError("tile extents not positive integers")
		if not (map_width >= 0 and map_height >= 0):
			raise ValueError("Map extents not positive integers")

		self._tile_dim = (tile_extent, tile_extent)
		# For now, we allow only a single tile atlast/ sprite sheet to be set
		self._map_dim = (map_width, map_height)
		# this is a map to the different grids		
		self._grid = {}

	@staticmethod
	def _tilemap_data_from(data, map_dim) -> []:
		# 1d or 2d data is turned into a 2D nested list representation
		map_width, map_height = map_dim
		_data = []
		_unique_indices = set([])

		if len(data) == map_width * map_height:
			# 1d case
			for y in range(map_height):
				x0, x1 = y * map_width, (y + 1) * map_width
				_yi = data[x0:x1]
				_data.append(_yi)
				if _yi not in _unique_indices:
					_unique_indices.add(_yi)
		elif len(data) == map_height:
			# 2d case
			_x0 = data[0]
			if not (len(_x0) == map_width):
				raise ValueError("Unknown Map format provided not a 1D or 2D (map height, map width) array")
			_data = data
			_unique_indices = set([_x for y in _data for _x in y])
		else:
			raise ValueError("Unknown Map format provided not a 1D or 2D (map height, map width) array")

		return _data, _unique_indices

	def add_grid(self, grid_name:str, data:list) -> TileMap:
		"""Sets a logical grid for our tile map.
		A logical grid is an arrangement of individual map tiles that define the behaviur of our world. If the
		world has already a logical grid with the same name set, then adding the new grid will raise an exception.

		Args:
				data (1D or 2D list of integers): Data defining the grid, which can be a 1D list of width*height tiles or
				a 2D nested list of the same dimensionality.

		Raises:
				ValueError: raises an exception if the visual grid data is not of the required dimensionality, or the name of the logical
				grid is either not provided or already taken.

		Returns:
				TileMap: The tile map with the logical grid added.
		"""		
		if not data:
			raise ValueError("no data provided")

		if not grid_name or grid_name.strip() == '':
			raise ValueError("grid name not provided")

		if grid_name in self._grid:
			raise ValueError("Grid type already present")

		_map_data, _unique_indices    = TileMap._tilemap_data_from(data, self._map_dim)
		self._grid[grid_name] = {"Grid": _map_data, "Indices": _unique_indices}

		return self

	@property
	def visual_grid_indices(self):
		return self._vgrid_index

	@property
	def tile_dimension(self):
		return self._tile_dim
	
	@property
	def tile_width(self):
		return self._tile_dim[0]
	
	@property
	def tile_height(self):
		return self._tile_dim[1]

	@property
	def map_dimension(self):
		return self._map_dim

	@property
	def map_width(self):
		return self._map_dim[0]

	@property
	def map_height(self):
		return self._map_dim[1]
	
	def has_grid(self, grid_name:str):
		if not grid_name or grid_name.strip() == '':
			raise ValueError("grid name not provided")
		return grid_name in self._grid

	def __iter__(self):
		return self._grid.__iter__()

	def __getitem__(self, k):
		return self.__getitem__(k)

	def __setitem__(self, k, v):
		return self.__setitem__(k, v)

	def __contains__(self, key):
		return self._grid.__contains__(key)

	def get_grid(self, grid_name:str):
		if not grid_name or grid_name.strip() == '':
			raise ValueError("grid name not provided")
		if grid_name not in self._logical_grid:
			raise ValueError("logical grid does not exist")
		return self._logical_grid[grid_name]["Grid"]

	def get_grid_indices(self, grid_name:str) -> {}:
		if not grid_name or grid_name.strip() == '':
			raise ValueError("grid name not provided")
		if grid_name not in self._logical_grid:
			raise ValueError("logical grid does not exist")
		return self._logical_grid[grid_name]["Indices"]

	def remove_grid(self, grid_name):
		if not grid_name or grid_name.strip() == '':
			raise ValueError("grid name not provided")
		if grid_name not in self._logical_grid:
			raise ValueError("logical grid does not exist")
		del(self._logical_grid[grid_name])
		return self

	def get_tile_index(self, grid_name:str, x:int, y:int):
		if not grid_name or grid_name.strip() == '':
			raise ValueError("Grid name not provided")
		if not (0 <= x <= self.map_width):
			raise ValueError("x coordinate outside of map dimensions")
		if not (0 <= y <= self.map_height):
			raise ValueError("y coordinate outside of map boundaries")
		return self._grid[grid_name]["Grid"][y][x]

	def empty_grid(self):
		_g = [self.map_width * [None] for _ in range(self.map_height)]
		return _g

	def __repr__(self):
		return "TileMap({}, {}) - Tiles({}, {})".format(self._map_dim[0], self._map_dim[1], self._tile_dim[0], self._tile_dim[1])