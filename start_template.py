# auth: christian bitter
# name: start_template
# desc: the starting template
# vers: 0.5

import pygame


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    pygame.init()

    w, h, t = 640, 480, "Elisa - <The Name of The Example>"
    c_white = (255, 255, 255)

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(c_white)

    fps_watcher = pygame.time.Clock()
    is_done = False

    while not is_done:
        elapsed_millis = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    main()
