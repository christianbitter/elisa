from __future__ import annotations

import os
import xml.etree.ElementTree
from uuid import uuid4

from .sprite import Sprite
from .spritesheet import SpriteSheet


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
# TODO: the grid properties are upper case and hardcoded


class TileMap(object):
    """A 2D Tile Map Structure"""

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

        self._id = uuid4()
        self._tile_dim = (tile_extent, tile_extent)
        # For now, we allow only a single tile atlast/ sprite sheet to be set
        self._map_dim = (map_width, map_height)
        # this is a map to the different grids
        self._grid = {}
        self._properties = {}

    @property
    def properties(self) -> map:
        return self._properties

    def add_property(self, k, v) -> TileMap:
        if not k:
            raise ValueError("Key not defined")
        self._properties[k] = v
        return self

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
                # potentially expand the set of unique indices
                for _elem in _yi:
                    if _elem not in _unique_indices:
                        _unique_indices.add(_elem)
        elif len(data) == map_height:
            # 2d case
            _x0 = data[0]
            if not (len(_x0) == map_width):
                raise ValueError(
                    "Unknown Map format provided not a 1D or 2D (map height, map width) array"
                )
            _data = data
            _unique_indices = set([_x for y in _data for _x in y])
        else:
            raise ValueError(
                "Unknown Map format provided not a 1D or 2D (map height, map width) array"
            )

        return _data, _unique_indices

    def add_grid(
        self, grid_name: str, data: list, visible: bool = True, props: dict = None
    ) -> TileMap:
        """Sets a logical grid for our tile map.
        A logical grid is an arrangement of individual map tiles that define the behaviur of our world. If the
        world has already a logical grid with the same name set, then adding the new grid will raise an exception.

        Args:
                        data (1D or 2D list of integers): Data defining the grid, which can be a 1D list of width*height tiles or
                        a 2D nested list of the same dimensionality.
                        grid_name (str): name of the grid
                        visible (bool): is this a visible layer
                        props (dict): additional properties (custom layer properties in tiled) to be added to the layer

        Raises:
                        ValueError: raises an exception if the visual grid data is not of the required dimensionality, or the name of the logical
                        grid is either not provided or already taken.

        Returns:
                        TileMap: The tile map with the logical grid added.
        """
        if not data:
            raise ValueError("no data provided")

        if not grid_name or grid_name.strip() == "":
            raise ValueError("grid name not provided")

        if grid_name in self._grid:
            raise ValueError("Grid type already present")

        _map_data, _unique_indices = TileMap._tilemap_data_from(data, self._map_dim)

        self._grid[grid_name] = {
            "Grid": _map_data,
            "Indices": _unique_indices,
            "Visible": visible,
            "Properties": props,
        }

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

    def visible_grids(self) -> list:
        """Returns a list of names of all visible grids

        Returns:
            list: list of grid names, if any
        """
        return [_name for _name in self._grid if self._grid[_name]["Visible"]]

    def has_grid(self, grid_name: str) -> bool:
        """Does this TileMap instance have a grid with the provided name.

        Args:
                        grid_name (str): Name of the sought grid.

        Raises:
                        ValueError: if the name is not provided or empty.

        Returns:
                        bool: True if there is at least one grid with the supplied name stored inside the
                                                TileMap instance
        """
        if not grid_name or grid_name.strip() == "":
            raise ValueError("grid name not provided")
        return grid_name in self._grid

    def has_visible(self) -> bool:
        """Determines if there is any visible grid stored in the TileMap instance

        Returns:
                        bool: True if there is at least one visible grid, else False.
        """
        bVis = [1 for g in self._grid if self._grid[g]["Visible"]]
        return len(bVis) > 0

    def __iter__(self):
        return self._grid.__iter__()

    def __getitem__(self, k):
        return self.__getitem__(k)

    def __setitem__(self, k, v):
        return self.__setitem__(k, v)

    def __contains__(self, key):
        return self._grid.__contains__(key)

    def get_grid(self, grid_name: str):
        if not grid_name or grid_name.strip() == "":
            raise ValueError("grid name not provided")
        if grid_name not in self._grid:
            raise ValueError("logical grid does not exist")
        return self._grid[grid_name]["Grid"]

    def get_grid_indices(self, grid_name: str) -> {}:
        if not grid_name or grid_name.strip() == "":
            raise ValueError("grid name not provided")
        if grid_name not in self._logical_grid:
            raise ValueError("logical grid does not exist")
        return self._logical_grid[grid_name]["Indices"]

    def remove_grid(self, grid_name):
        if not grid_name or grid_name.strip() == "":
            raise ValueError("grid name not provided")
        if grid_name not in self._logical_grid:
            raise ValueError("logical grid does not exist")
        del self._logical_grid[grid_name]
        return self

    def get_tile_index(self, grid_name: str, x: int, y: int):
        if not grid_name or grid_name.strip() == "":
            raise ValueError("Grid name not provided")
        if not (0 <= x <= self.map_width):
            raise ValueError("x coordinate outside of map dimensions")
        if not (0 <= y <= self.map_height):
            raise ValueError("y coordinate outside of map boundaries")
        return self._grid[grid_name]["Grid"][y][x]

    def grid_names(self) -> list:
        return [g for g in self._grid]

    def empty_grid(self):
        _g = [self.map_width * [None] for _ in range(self.map_height)]
        return _g

    def __repr__(self):
        return "TileMap[{}]({}, {}) - Tiles({}, {}); {} Layers".format(
            self._id,
            self._map_dim[0],
            self._map_dim[1],
            self._tile_dim[0],
            self._tile_dim[1],
            len(self._grid),
        )


def tileprops_from_tsx(tsx_fp: str, reserve_index_zero: bool = True, **kwargs) -> dict:
    """Creates the tile set properties from the underlying tsx file.

    Args:
        tsx_fp (str): path to the tile set descriptor xml file.
        reserve_index_zero (bool, optional): defines if the 0 index in the properties map is reserved for the internal NO-TILE tile. If set to true,
        the tile with id 0 will have type = __RESERVED__ and all tile types defined in the tsx file will start at index 1. If set to False,
        all tile types defined in the tsx file will start at ID = 0 and no NO-TILE is inserted. Defaults to True.

    Raises:
        ValueError: if no tsx file path is provided, the file does not exist at the respective path, or this does not point to a tsx file.

    Returns:
        dict: a map of tile id to their respective properties
    """
    if not tsx_fp or tsx_fp.strip() == "":
        raise ValueError("tile set path not provided")
    if not os.path.exists(tsx_fp):
        raise ValueError("tile set path does not exist")
    if not tsx_fp.endswith(".tsx"):
        raise ValueError("tile set descriptor tsx file not provided")

    verbose = kwargs.get("verbose", False)
    tsx_dir_fp = os.path.dirname(tsx_fp)

    if verbose:
        print(f"tsx file located under {tsx_dir_fp}")

    root = xml.etree.ElementTree.parse(tsx_fp).getroot()
    tile_props = root.findall("tile")

    props = {}
    start_at = 0

    if reserve_index_zero:
        props[0] = {"type": "__RESERVED__"}
        start_at = 1

    for tp in tile_props:
        _id = start_at + int(tp.attrib["id"])
        props[_id] = {"type": tp.attrib["type"]}

    return props


def tilemap_from_tiled(tsm_fp: str, **kwargs) -> tuple:
    """Returns a three tuple composed of tile map, path to referenced tileset descriptors built in TileEd and all of the defined properties,
    i.e. tm, tileset_descs, tileprops.

    Any custom property referenced in the tsm file is added as a TileMap property.
    Any layer referenced under the tsm layers is added as a layer to the TileMap.
    It is assumed that the layer names are uniques, and that the layer dimensionality is
    the same as the TileMap dimensionality.

    Args:
                    tsm_fp (str): Path to the tiled tilemap tsm file

    Raises:
                    ValueError: if the tilemap path is not provided, or does not exist.
                    ValueError: if the map is not built right-down
                    ValueError: if non-orthogonal orientation is used in the tile map
                    ValueError: if tiles are non-square (e.g., tile width must equal tile height)
                    ValueError: if a referenced layer is not of the dimensionality indicated on the tile map.

    Returns:
                    tuple: a tuple consisting of a TileMap instance, any number of tileset file references and tile object type references (list of dict)
                    These can be used to build the relevant SpriteSheet or TextureAtlas objects.
    """
    if not tsm_fp or tsm_fp.strip() == "":
        raise ValueError("tile map path not provided")
    if not os.path.exists(tsm_fp):
        raise ValueError("tile map path does not exist")

    verbose = kwargs.get("verbose", False)
    tsm_dir_fp = os.path.dirname(tsm_fp)
    root = xml.etree.ElementTree.parse(tsm_fp).getroot()

    orientation = root.attrib["orientation"]
    if orientation != "orthogonal":
        raise ValueError("Only orthogonal orientation supported")

    renderorder = root.attrib["renderorder"]
    if renderorder != "right-down":
        raise ValueError("Ony renderorder right-down supported")

    width = int(root.attrib["width"])
    height = int(root.attrib["height"])

    tilewidth = int(root.attrib["tilewidth"])
    tileheight = int(root.attrib["tileheight"])

    if tilewidth != tileheight:
        raise ValueError("tile width and tile height need to match")

    infinite = int(root.attrib["infinite"])
    nextlayerid = int(root.attrib["nextlayerid"])
    nextobjectid = int(root.attrib["nextobjectid"])

    if verbose:
        print(
            f"Tilemap defines (infinite, nextlayerid, nextobjectid) - will be ignored: {infinite}, {nextlayerid}, {nextobjectid}"
        )

    custom_props = root.findall("properties/*")
    tilesets = root.findall("tileset")
    layers = root.findall("layer")

    tm = TileMap(tile_extent=tilewidth, map_width=width, map_height=height)
    for p in custom_props:
        tm.add_property(p.attrib["name"], p.attrib["value"])

    # add the different layers
    for _a_layer in layers:
        layer_id = _a_layer.attrib["id"]
        layer_name = _a_layer.attrib["name"]
        layer_width = int(_a_layer.attrib["width"])
        layer_height = int(_a_layer.attrib["height"])
        layer_visible = int(_a_layer.attrib.get("visible", 1)) != 0

        layer_custom_props = None

        if layer_width != width:
            raise ValueError(
                f"Layer {layer_id} cannot have different width than global tile map width"
            )
        if layer_height != height:
            raise ValueError(
                f"Layer {layer_id} cannot have different height than global tile map height"
            )

        props_node = _a_layer.findall("properties/*")
        if props_node and len(props_node) > 0:
            layer_custom_props = {}
            for p in props_node:
                layer_custom_props[p.attrib["name"]] = p.attrib["value"]

        layer_data = _a_layer.findall("data")[0]
        layer_enc = layer_data.get("encoding")
        if layer_enc != "csv":
            raise ValueError("Encoding must be csv")
        grid_data = [
            int(v)
            for _l_data in layer_data.text.splitlines()
            for v in _l_data.split(",")
            if v.strip() != ""
        ]
        tm.add_grid(layer_name, grid_data, layer_visible, layer_custom_props)

    tileset_descs = [os.path.join(tsm_dir_fp, _ts.attrib["source"]) for _ts in tilesets]

    tileprops = [tileprops_from_tsx(desc_fp, **kwargs) for desc_fp in tileset_descs]

    return tm, tileset_descs, tileprops
