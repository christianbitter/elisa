# name: elisa_19_0_-_polys_and_AABB.py
# auth: (c) 2020 christian bitter
# desc: implement axis aligned bounding boxes for our polygon.
#       implement simple transformation of the AABB
# References:
# Computer Science 420 (University of San Francisco): Game Engineering
# https://www.cs.usfca.edu/~galles/cs420S13/lecture/intersection2D.pdf

# TODO: documentation

# NOTE: QuadTree rebalancing will be done when moved into Elisa

from __future__ import annotations

import pygame

from elisa.linalg import Poly2, Rect2


def on_quit():
    print("Elisa -> Quit()")


def main():
    # init is a convenient way to initialize all subsystems
    # instead we could also initialize the submodules directly - for example by calling pygame.display.init(), pygame.display.quit()
    no_pass, no_fail = pygame.init()

    if no_fail > 0:
        print("Not all pygame modules initialized correctly")
        print(pygame.get_error())
    else:
        print("All pygame modules initializes")

    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")
    if not pygame.display:
        print("Pygame - display not loaded")
    if not pygame.mouse:
        print("Pygame - mouse not loaded")

    print("Did we initialize: {}".format(pygame.get_init()))
    print("Pygame Version: {}".format(pygame.ver))
    print("Pygame runs on SDL Version: {}".format(pygame.get_sdl_version()))
    print("Pygame Display Driver: {}".format(pygame.display.get_driver()))

    pygame.register_quit(on_quit)

    w, h, t = 640, 480, "Elisa - 19.1 Collision Detection - QuadTree"
    c_white = (255, 255, 255)
    c_black = (0, 0, 0)

    screen_buffer = pygame.display.set_mode(size=(w, h), flags=0)
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(c_white)

    # here we setup a pygamer clock - we will discuss this in a later example
    fps_watcher = pygame.time.Clock()
    is_done = False

    # we compose a scene of ...
    while not is_done:
        _ = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

        back_buffer.fill(c_black)

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
