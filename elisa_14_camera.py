# auth: christian bitter
# name: elisa_14_camera.py
# desc: a simple 2d orthographic camera, that allows us to focus on different things on the screen
#       enabling an artistic effect.
#
# TODO: the scene is a mountain range background
# TODO: elisa is set at some position
# TODO: the camera is fixed
# TODO: only the camera visible portion of the screen is rendered
# TODO:

# https://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame

import pygame

# TODO: elisa_14_camera.py

def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    pygame.init()

    S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Elisa - Virtual Camera"
    C_WHITE = (255, 255, 255)

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
            if event.type == pygame.QUIT:
                is_done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                pass
            else:
                pass
