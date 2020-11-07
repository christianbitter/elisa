# auth: christian bitter
# desc: this will combine elisa 7 and 6 by having a movable character in an environment generated from a sprite map
#       the character can move around according to the simple constraints
#       imposed by the environment. That is, this tutorial will support
#           An abstraction for maps
#               TODO: a tiled map is built from a 2d array of map tiles
#               TODO: map tiles are identifiable unique game objects
#               TODO: a map tile links some structural game-relevant properties and a visual representation
#           TODO: on habitable tiles player moves from tile to tile (simple movement not necessarily animation)
#           TODO: player cannot run into walls
#           TODO: expand the animation concept from frame iteration to an animation composed of sprites
#       In this example we keep the data and rendering close, but at a later stage (particle system),
#       the data holding map and rendering map renderer is broken.

import os
import pygame
from pygame.locals import *
import json

# gfx: https://ansimuz.itch.io/tiny-rpg-town
# sprite packing: https://www.leshylabs.com/apps/sstool/

# TODO: elisa_8

def tileno2spritemap(tileno, sprite_map):
    tile_id = "grass_{}".format(tileno)
    return sprite_map[tile_id]


def render_map(buffer, sprite_map, world_map, start_x, start_y, map_width = 10, map_height = 10):
    i_idx = 0
    _y = start_y
    for y in range(map_height):
        _x = start_x
        for x in range(map_width):
            tile_no = world_map[i_idx]
            sprite_def = tileno2spritemap(tile_no, sprite_map)
            buffer.blit(sprite_def.image, (_x, _y))
            i_idx += 1
            _x = _x + sprite_def.width
        _y = _y + sprite_def.height #


class MapTile(dict):
    """Since a map tile is mostly structural properties, and we wish to serialize it into JSON,
    let's make it inherit from dict and get serialization out of the box
    """
    def __repr__(self):
        return "MapTile"


class TiledMap(object):
    """"""

    def __init__(self):
        """Constructor for Map"""
        super(TiledMap, self).__init__()
        self._map = None  # map is the actual map data
        self._tile_def = None  # tile def links a specific tile referenced in the map to a definition
        self._width = 0
        self._height = 0

    @staticmethod
    def __check_tile_ids(the_map, tile_def):
        tile_ids = set(the_map)
        if len(tile_ids) != len(tile_def):
            raise ValueError("number of referenced tiles != number of defined tiles")

        for an_id in tile_ids:
            if an_id not in tile_def.keys():
                raise ValueError("tile definition does not contain definition for {}".format(an_id))

        return True

    @staticmethod
    def from_1d(a_map: list, width: int, height: int, tile_def: dict):
        if not a_map:
            raise ValueError("Map missing")
        if width is None:
            raise ValueError("Width missing")
        if width < 1:
            raise ValueError("Width <= 0")
        if height is None:
            raise ValueError("Height missing")
        if height < 1:
            raise ValueError("Height <= 0")
        if not tile_def:
            raise ValueError("Tile Definition missing")

        wh = width*height

        if len(a_map) != wh:
            raise ValueError("Map does not contain suffient tiles")
        m = TiledMap()
        m._width = width
        m._height = height
        m._map = a_map
        _ = TiledMap.__check_tile_ids(the_map=a_map, tile_def=tile_def)
        m._tile_def = tile_def

        return m

    @property
    def map_data(self):
        return self._map

    @staticmethod
    def from_2d(a_map:list, tile_def:dict):
        if not a_map:
            raise ValueError("Map missing")
        if not tile_def:
            raise ValueError("Tile Definition missing")

        _height = len(a_map)
        entry_0 = a_map[0]
        if not isinstance(entry_0, list):
            raise ValueError("Map is not 2-D - map[][]")
        _width = len(entry_0)

        for r in a_map:
            if not isinstance(r, list):
                raise ValueError("Map is not 2-D - map[][]")
            if len(r) != _width:
                raise ValueError("Uneven map segments/ differing width")

        wh = _width * _height
        m = TiledMap()
        l_map = [xy for y_row in a_map for xy in y_row]
        assert(len(l_map) == wh)
        m._map = l_map
        m._width = _width
        m._height = _height

        _ = TiledMap.__check_tile_ids(the_map=l_map, tile_def=tile_def)
        m._tile_def = tile_def
        return m

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def serialize(self):
        pass

    def deserialize(self):
        pass

    def load(map_fp:str):
        # TODO: load from json structure
        pass

    def save(self, save_fp: str):
        if not save_fp:
            raise ValueError("save file path not provided")
        with open(save_fp, 'w+', encoding='ascii') as f:
            json_dict = {
                "map": self._map,
                "tile_def": self._tile_def,
                "width": self._width,
                "height": self._height
            }
            json.dump(json_dict, f)

    def __repr__(self):
        return "Map - Width: {}/ Height: {}".format(self._width, self._height)


def main():
    if not pygame.font: print("Pygame - fonts not loaded")
    if not pygame.mixer: print("Pygame - audio not loaded")

    # init pygame - create the main window, and a background surface
    pygame.init()

    world_map = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 3, 1, 3, 1, 3, 1, 3, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 3, 1, 3, 1, 3, 1, 3, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 3, 1, 3, 1, 3, 1, 3, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 3, 1, 3, 1, 3, 1, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    wall_tile = MapTile()
    way1_tile = MapTile()
    flower1_tile = MapTile()

    a_map = TiledMap.from_2d(world_map, tile_def={1: wall_tile,
                                                  2: way1_tile,
                                                  3: flower1_tile})

    a_map_fp = "test_json.json"
    a_map.save(a_map_fp)

    MAP_WIDTH, MAP_HEIGHT = 10, 10
    MAP_OFFSET_X, MAP_OFFSET_Y = 50, 50

    S_WIDTH = 800
    S_HEIGHT= 600
    S_TITLE = "Elisa8 - Moving in an Environment"

    C_WHITE = (250, 250, 250)
    C_BLUE = (0, 0, 255)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    is_done = False

    while not is_done:

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

        back_buffer.fill(C_WHITE)
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()
