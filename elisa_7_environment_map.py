# auth: christian bitter
# desc: create a simple map showing some environment for elisa to move in.

import os, sys
import pygame
from pygame.locals import *
import json

# gfx: https://ansimuz.itch.io/tiny-rpg-town
# sprite packing: https://www.leshylabs.com/apps/sstool/

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


def load_image(fp, colorkey=None, image_only=False):
    if not fp:
        raise ValueError("load_image - fp not provided")

    fullname = os.path.join(fp)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', fp)
        raise SystemExit(message)

    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)

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
        print('Cannot load image:', fullname)
        raise SystemExit(message)
    if image_only:
        return image
    else:
        return image, image.get_rect()

class PSprite(object):
    def __init__(self, id, w, h, img):
        super(PSprite, self).__init__()
        self._id = id
        self._width = w
        self._height = h
        self._image = img

    @property
    def id(self):
        return self._id

    @property
    def image(self):
        return self._image

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


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

    def initialize(self):
        if not self._initialized:
            with open(self._descriptor, mode='r+') as fp:
                self._sprite_map = json.load(fp)

            if 'id' not in self._sprite_map: raise ValueError("SpriteMap - id missing")
            if 'width' not in self._sprite_map: raise ValueError("SpriteMap - width missing")
            if 'height' not in self._sprite_map: raise ValueError("SpriteMap - height missing")
            if 'image_path' not in self._sprite_map: raise ValueError("SpriteMap - image path missing")
            if 'no_sprites' not in self._sprite_map: raise ValueError("SpriteMap - no_sprites missing")
            self._id = self._sprite_map['id']
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
            for i, sprite_def in enumerate(sprites):
                id = sprite_def['id']
                x = sprite_def['x']
                y = sprite_def['y']
                w = sprite_def['width']
                h = sprite_def['height']
                sprite_img = self._image.subsurface(x, y, w, h)
                self._sprites[id] = PSprite(id, w, h, sprite_img)

            if self._no_sprites > 0 and self._no_sprites != len(self._sprites):
                raise ValueError("Number of defined sprites does not match declared sprites")
            self._initialized = True

    def __getitem__(self, item):
        if not item:
            raise ValueError("SpriteMap.get - key not provided")
        if item in self._sprites:
            return self._sprites[item]
        else:
            raise ValueError("SpriteMap.get - undefined sprite selected")


def main():
    if not pygame.font: print("Pygame - fonts not loaded")
    if not pygame.mixer: print("Pygame - audio not loaded")

    # init pygame - create the main window, and a background surface
    pygame.init()

    world_map = [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 2, 2, 2, 2, 2, 2, 2, 2, 1,
        1, 1, 3, 1, 3, 1, 3, 1, 3, 1,
        1, 2, 2, 2, 2, 2, 2, 2, 2, 1,
        1, 1, 3, 1, 3, 1, 3, 1, 3, 1,
        1, 2, 2, 2, 2, 2, 2, 2, 2, 1,
        1, 1, 3, 1, 3, 1, 3, 1, 3, 1,
        1, 2, 2, 2, 2, 2, 2, 2, 2, 1,
        1, 1, 3, 1, 3, 1, 3, 1, 3, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1
    ]

    MAP_WIDTH, MAP_HEIGHT = 10, 10
    MAP_OFFSET_X, MAP_OFFSET_Y = 50, 50

    S_WIDTH = 800
    S_HEIGHT= 600
    S_TITLE = "Elisa7 - Drawing a Map using a Sprite Sheet"

    C_WHITE = (250, 250, 250)
    C_BLUE = (0, 0, 255)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    # FPS watcher
    fps_watcher = pygame.time.Clock()
    is_done = False

    grass_sprite_map = SpriteMap("asset/tileset_grass.json")
    grass_sprite_map.initialize()

    while not is_done:
        fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

        back_buffer.fill(C_WHITE)
        render_map(back_buffer, grass_sprite_map, world_map, MAP_OFFSET_X, MAP_OFFSET_Y, MAP_WIDTH, MAP_HEIGHT)
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()
