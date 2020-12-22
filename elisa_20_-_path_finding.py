# auth: christian bitter
# name: elisa_20_-_path_finding.py
# desc:
# this is the first example on simple path finding
# TODO: create tile map
# TODO: create player
# TODO: create goal to attain
# TODO: naive path finding so that the player attains the goal

# asset credit: Mozilla and https://developer.mozilla.org/en-US/docs/Games/Techniques/Tilemaps
# asset credit: Elise Sprite TODO:
# in order to create tile sets, you may find the following helpful:
# sprite packing: https://www.leshylabs.com/apps/sstool/

import json
import os

import pygame
from pygame.locals import QUIT

from elisa.arch.sm import State, StateMachine, Transition
from elisa.sprite import (Sprite, SpriteAnimation, SpriteSheet, Tile, TileMap,
                          spritesheet_from_tiled, tilemap_from_tiled)


class TileMapRenderer(object):
    C_WHITE = (255, 255, 255)

    def __init__(
        self,
        tile_map: TileMap,
        tile_atlas: SpriteSheet,
        world_x: int,
        world_y: int,
        view_width: int,
        view_height: int,
    ):
        super(TileMapRenderer, self).__init__()
        if not tile_map:
            raise ValueError("Tile map not provided")
        if not tile_atlas:
            raise ValueError("Tile Atlas not provided")
        if not tile_atlas.initialized:
            raise ValueError("Tile Atlas not initialized")
        if not tile_map.has_visible():
            raise ValueError("No visual layer registered in the tile map")

        self._tile_map = tile_map
        self._tile_atlas = tile_atlas
        self._index2sprite = {
            0: None,
            1: "test_tiled_tileset_0",  # grass
            2: "test_tiled_tileset_1",  # "mud_1"
            3: "test_tiled_tileset_2",  # "tree_1"
            4: "test_tiled_tileset_3",  # incomplete tree top
            5: "test_tiled_tileset_4",  # bush
        }
        self._clear_colour = TileMapRenderer.C_WHITE

        self._tile_width = self._tile_map.tile_dimension[0]
        self._tile_height = self._tile_map.tile_dimension[1]

        self._empty_tile = pygame.surface.Surface(self._tile_map.tile_dimension)
        self._view_width = view_width
        self._view_height = view_height
        self._x = world_x
        self._y = world_y

    def clear_buffer(self, surface):
        surface.fill(self._clear_colour)

    def render(self, surface):
        self.clear_buffer(surface)

        _x0, _y0 = self._x, self._y

        for y in range(self._tile_map.map_height):
            _x0 = self._x

            # very primitive do not render anything strictly outside of the visible bounds
            if _y0 >= self._view_height or _x0 >= self._view_width:
                continue

            for x in range(self._tile_map.map_width):
                ti = self._tile_map.get_tile_index("Tile Layer 1", x, y)
                ta_i = self._index2sprite.get(ti, 0)

                if ti == 0:
                    tile_i = self._empty_tile
                # TODO: this should be a more elaborate check for a different layer
                elif ti == 4 or ti == 5:
                    # blit grass and then the other tile
                    pSprite = self._tile_atlas[self._index2sprite[1]]
                    surface.blit(pSprite.as_pygame_sprite, (_x0, _y0))

                    pSprite = self._tile_atlas[ta_i]
                    tile_i: Sprite = pSprite.as_pygame_sprite
                else:
                    pass

                pSprite = self._tile_atlas[ta_i]
                tile_i: Sprite = pSprite.as_pygame_sprite
                surface.blit(tile_i, (_x0, _y0))

                _x0 += self._tile_width
            _y0 += self._tile_height


def build_world():
    # TODO: load the tile map from the tmx file
    tm_fp = "C:/Development/repos/python_projects/games/tileed/test_tiled_tileset.tmx"
    tm, assets, props = tilemap_from_tiled(tm_fp)
    tileset = spritesheet_from_tiled(assets[0], verbose=True)
    return tm, tileset


def main():
    pygame.init()

    MAP_OFFSET_X, MAP_OFFSET_Y = 50, 50

    C_WHITE = (255, 255, 255)
    S_WIDTH = 800
    S_HEIGHT = 600
    S_TITLE = "Elisa 20 - Path finding"

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    world, tileatlas = build_world()
    tm_renderer = TileMapRenderer(
        world,
        tileatlas,
        world_x=MAP_OFFSET_X,
        world_y=MAP_OFFSET_Y,
        view_width=S_WIDTH,
        view_height=S_HEIGHT,
    )

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    fps_watcher = pygame.time.Clock()
    is_done = False

    while not is_done:
        _ = fps_watcher.tick(24)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

        tm_renderer.render(back_buffer)
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main()
