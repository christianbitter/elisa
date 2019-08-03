# auth: christian bitter
# name: elisa_15_parallax_mapping
# desc: a simple parallax mapping example ...
#       we load the layers of a parallax mapped background separately
#       the arrow keys allow going left and right
# vers: 0.1

import pygame
import os, sys
from sprites import load_png, PSprite


def load_images(target_width: int = 640, target_height: int = 480):
    img_container = {}
    ckey = (255, 255, 255, 0)
    img_base_path = "asset/gfx/raventale_parallax_backgound"

    for img_name in os.listdir(img_base_path):
        if not img_name.endswith('.png'):
            continue
        image_fp = os.path.join(img_base_path, img_name)
        img = load_png(image_fp, image_only=True)
        img = pygame.transform.scale(img, (target_width, target_height))
        img_container[img_name] = img

    print("Loaded {} images ...".format(len(img_container)))
    img_order = [
        '_11_background.png',  # the background is full scale, it needs to be drawn first to not occlude the rest
        '_10_distant_clouds.png', '_09_distant_clouds1.png', '_08_clouds.png', '_07_huge_clouds.png',
        '_05_hill1.png', '_06_hill2.png',
        '_04_bushes.png',
        '_03_distant_trees.png',
        '_02_trees and bushes.png',
        '_01_ground.png'
    ]
    return img_container, img_order

def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    pygame.init()

    w, h, t = 640, 480, "Elisa - 15 Parallax Mapping"
    c_white = (255, 255, 255)
    c_black = (0, 0, 0, 255)

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    background, bg_order = load_images()

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size(), pygame.SRCALPHA)
    img_surface = pygame.Surface(screen_buffer.get_size(), pygame.SRCALPHA)

    # back_buffer = back_buffer.convert()
    back_buffer.fill(c_black)

    fps_watcher = pygame.time.Clock()
    is_done = False

    while not is_done:
        elapsed_millis = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

        # show the background ...
        # back_buffer.fill(c_black)
        for k in bg_order:
            back_buffer.blit(background[k], (0, 0))

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    main()
