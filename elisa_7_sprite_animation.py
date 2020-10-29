# auth: christian bitter
# desc: based on the previous elisa, we will now look into better definition of animation.
#       additionally, we reuse the SpriteManager that has been integrated into the package itself
#       animation will be attached to timings and so on

from pygame.locals import *
import os
from elisa.sprite import SpriteSheet

import pygame

# TODO: elisa 7
# TODO: The sprite animation
# This example will focus on Sprite Map/ Sheet based animations.
# That is, a sprite map can be defined based on 
# (i) some single image source where the image contains all sprites relevant
# (ii) or via a sequence of individual images where each image defines a sprite that takes part in the animation, 
# (iii) or via surfaces defined in a texture/ sprite atlas

def main():
    if not pygame.font: print("Pygame - fonts not loaded")
    # init pygame - create the main window, and a background surface
    pygame.init()
    
    sprite_sheet = SpriteSheet("asset/sprite_sheet_grass.json")

    S_WIDTH = 800
    S_HEIGHT= 600
    S_TITLE = "Elisa - Statemachine and GFX"

    C_WHITE = (250, 250, 250)
    C_BLUE = (0, 0, 255)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    sprite_sheet.initialize(verbose=True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    # FPS watcher
    fps_watcher = pygame.time.Clock()
    is_done = False

    while not is_done:
        fps_watcher.tick(25)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

            key_map = pygame.key.get_pressed()

        back_buffer.fill(C_WHITE)
        # back_buffer.blit(sprite_sheet.image, (0, 0))
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()
