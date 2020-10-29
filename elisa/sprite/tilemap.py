from __future__ import annotations
from .sprite import Tile

import enum
# for starters we closely follow: https://developer.mozilla.org/en-US/docs/Games/Techniques/Tilemaps
# TODO: 1 to many tile atlas - this serves as our repository of visual tiles
# an index from the tile atlas tile to the visual grid needs to be established
# TODO: set tile at coords for the visual and the logical tile
class TileMap(object):
	"""A 2D Tile Map Structure
	"""
	def __init__(self, tile_width: int, tile_height: int, map_width: int, map_height: int):
		super(TileMap, self).__init__()

		if not (tile_width >= 0 and tile_height >= 0):
			raise ValueError("tile extents not positive integers")
		if not (map_width >= 0 and map_height >= 0):
			raise ValueError("Map extents not positive integers")
		if not (tile_width <= map_width and tile_height <= map_height):
			raise ValueError("Tile extents not a factor map extent")

		self._tile_dim = (tile_width, tile_height)
		self._tile_atlas = []
		self._map_dim = (map_width, map_height)
		# the visual grid is the abstract representation of our map which is going to be rendered
		# this is a 2d array of h * w
		self._visual_grid = []
		# logical grid is a map, holding potentially man different grids
		# this is a 2d array of h * w
		self._logical_grid = {}		

	@staticmethod
	def _tilemap_data_from(data, map_dim) -> []:
		# 1d or 2d data
		map_width, map_height = map_dim
		_data = []

		if len(data) == map_width * map_height:
			# 1d case
			for y in range(map_height):
				x0, x1 = y * map_width, (y + 1) * map_width
				_yi = data[x0:x1]
				_data.append(_yi)
		elif len(data) == map_height:
			# 2d case
			_x0 = data[0]
			if not (len(_x0) == map_width):
				raise ValueError("Unknown Map format provided not a 1D or 2D (map height, map width) array")
			_data = data
		else:
			raise ValueError("Unknown Map format provided not a 1D or 2D (map height, map width) array")

		return _data

	def add_visual_grid(self, data) -> TileMap:
		if not data:
			raise ValueError("no data provided")
		self._visual_grid = TileMap._tilemap_data_from(data, self._map_dim)
		return self

	def add_logical_grid(self, grid_name, data) -> TileMap:
		if not data:
			raise ValueError("no data provided")

		if not grid_name or grid_name == '':
			raise ValueError("grid name not provided")

		if grid_name in self._logical_grid:
			raise ValueError("Grid type already present")

		_data = TileMap._tilemap_data_from(data, self._map_dim)
		self._logical_grid[grid_name] = _data

		return self

	def add_tile_atlas(self, atlas_desc_fp:str) -> TileMap:
		return self

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
	
	@property
	def visual_grid(self):
		return self._visual_grid

	@property
	def logical_grid(self):
		return self._logical_grid

	def get_logical_grid(self, grid_name):
		if not grid_name or grid_name == '':
			raise ValueError("grid name not provided")
		if grid_name not in self._logical_grid:
			raise ValueError("logical grid does not exist")
		return self._logical_grid[grid_name]

	def remove_logical_grid(self, grid_name):
		if not grid_name or grid_name == '':
			raise ValueError("grid name not provided")
		if grid_name not in self._logical_grid:
			raise ValueError("logical grid does not exist")
		del(self._logical_grid[grid_name])
		return self

	def __repr__(self):
		return "TileMap({}, {}) - Tiles()".format(self._map_dim[0], self._map_dim[1], self._tile_dim[0], self._tile_dim[1])