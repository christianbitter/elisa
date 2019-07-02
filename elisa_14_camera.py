# auth: christian bitter
# name: elisa_14_camera.py
# desc: a simple 2d orthographic camera, that allows us to focus on different things on the screen
#       enabling an artistic effect.
#
#       TODO: The scene is a simple raining environment, mountain range like background, with raindrops falling off
#       TODO: The user can use the mouse and click in the scene.
#       TODO: When clicked in the scene, the camera directs focus to the area clicked and magnifies the area so that
#        the majority of the render area is covered with that portion of the screen.

# https://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame

import pygame

# TODO: elisa_14_camera.py

def main():
    if not pygame.font: print("Pygame - fonts not loaded")
    if not pygame.mixer: print("Pygame - audio not loaded")

    # init pygame - create the main window, and a background surface

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