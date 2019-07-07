# auth: christian bitter
# name: start_template.py
# desc: the starter template for all physics explorations. based off the elisa starter template.

import pygame


def main():
    if not pygame.font: print("Pygame - fonts not loaded")
    if not pygame.mixer: print("Pygame - audio not loaded")

    pygame.init()

    S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Physx - <The Name of The Example>"
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
            else:
                pass

        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__':
    main()

