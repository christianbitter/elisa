# auth: christian bitter
# desc: this will combine elisa 7 and 6 by having a movable character
#       in an environment generated from a sprite map
#       the character can move around according to the simple constraints
#       imposed by the environment. That is, this tutorial will support
#           TODO: abstraction for maps
#           TODO: player moves from tile to tile (simple movement not necessarily animation)
#           TODO: player cannot run into walls
#           TODO: expand the animation concept from frame iteration to an animation composed of sprites

import os
import pygame
from pygame.locals import *
import json

# gfx: https://ansimuz.itch.io/tiny-rpg-town
# sprite packing: https://www.leshylabs.com/apps/sstool/

# TODO: elisa_9

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


# The sprite animation
#
# We animate sprites by composing a sequence of pictures across time. Different types of animation may exist:
# Single Frame - one frame is defined and always repeated
# Frame Sequence - there can be many frames, the user has to specify how each sprite maps to a particular frame number
#                  under the assumption of defined frame rate. For example, the user may specify
#                  play sprite0 for 8 frames, then spriteN for another 8 frames and close it out by playing SpriteM for the rest
#                  of 9 frames.
# Procedural - the user defines a set of frames at most no frames in no frames per second framerate, i.e. 25 frames or similar.
#
# Repeat - will set the state of the animation back to zero, after the end of the animation is reached
# Sprites can be registered from any sprite map source or image source
# Each update step we move the current frame index. If the frame index reaches the last. If repeat is switched on
# the repeat will trigger an update of the current frame index, otherwise the i

class Map():
    """"""

    def __init__(self, ):
        """Constructor for Map"""
        super(Map, self).__init__()

    def load(map_fp:str):
        pass

    def save(map_obj:Map):
        pass

    def render_minimap(self):
        pass

    def render(self):
        pass


class SpriteAnimation(object):
    """"""

    def __init__(self, sprite_def:list, frame_def:list, repeat_index: int = -1):
        """Constructor for SpriteAnimation"""
        super(SpriteAnimation, self).__init__()
        self._sprites = sprite_def
        self._frames  = frame_def
        self._frame_index = 0

        # TODO: a sprite def is just a sprite
        # TODO: check that number of sprite and frame defs line up
        # TODO: check repeat index either -1 or a valid frame index
        self._repeat_index = repeat_index

    def next_frame(self):
        self._frame_index = self._frame_index + 1
        if self.repeats and self._frame_index >= self._repeat_index:
            self._frame_index = 0

    def render(self, buffer):
        pass

    @property
    def repeats(self):
        return self._repeat_index > -1


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
    S_TITLE = "Elisa8 - Sprite Animations"

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


    while not is_done:
        fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

        back_buffer.fill(C_WHITE)
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()
