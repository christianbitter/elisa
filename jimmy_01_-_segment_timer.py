# auth: christian bitter
# name: jimmy_01_-_segment_timer.py
# desc: a digital 60 second timer via a segment display

# TODO: jimmy needs to move to his own space, depending on the library

import pygame
from elisa import uifx


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    # init pygame - create the main window, and a background surface

    pygame.init()

    w, h, t = 640, 480, "Jimmy - 01 Segment Timer>"
    c_white = (255, 255, 255)

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(c_white)

    tdc = uifx.TwoDigitCounter(x=100, y=100, name='tdc', initial_value=60, colour=(64, 224, 64, 255))
    # tdc = uifx.SegmentDisplay(x=100, y=100, value=1, colour=(64, 224, 64, 255), size='medium')
    allsprites = pygame.sprite.RenderPlain(tdc)

    # FPS watcher
    fps_watcher = pygame.time.Clock()
    is_done = False

    ds = 0

    while not is_done:
        ds = ds + fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True

        if ds > 1000:
            tdc.tick()
            ds -= 1000
        tdc.update()
        back_buffer.fill(color=(0, 0, 0, 255))
        allsprites.draw(back_buffer)
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__':
    main()
