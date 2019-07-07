# auth: christian bitter
# name: elisa_12_1_blending.py
# desc:
# this tests the blending of a sprite onto background, using various blend modes

import pygame
from enum import Enum, IntFlag
from sprites import SpriteMap

def main():

    if not pygame.font: raise("Pygame - fonts not loaded")
    if not pygame.mixer: print("Pygame - audio not loaded")

    # init pygame - create the main window, and a background surface

    pygame.init()

    S_WIDTH = 640
    S_HEIGHT= 480
    S_TITLE = "Elisa 12-1 - Blending of sprites"

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)

    is_done = False
    alpha = 0
    while not is_done:
        pygame.time.delay(100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break
            else:
                pass

        s0 = pygame.Surface((200, 200), pygame.SRCALPHA)  # per-pixel alpha
        s0.fill((255, 0, 0, 64))  # notice the alpha value in the color

        s1 = pygame.Surface((200, 200), pygame.SRCALPHA)
        s1.fill((0, 255, 0, 64))

        s2 = pygame.Surface((50, 50), pygame.SRCALPHA)
        s2.fill((0, 0, 255, 16))

        s3 = pygame.Surface((50, 50), pygame.SRCALPHA)
        s3.fill((0, 0, 255, 32))

        s4 = pygame.Surface((50, 50), pygame.SRCALPHA)
        s4.fill((0, 0, 255, 64))

        s5 = pygame.Surface((50, 50), pygame.SRCALPHA)
        s5.fill((0, 0, 255, 128))

        screen_buffer.fill((0, 0, 0, 0))
        screen_buffer.blit(s0, (100, 100))
        screen_buffer.blit(s1, (250, 50))
        screen_buffer.blit(s2, (100, 100))
        screen_buffer.blit(s3, (150, 150))
        screen_buffer.blit(s4, (200, 200))
        screen_buffer.blit(s5, (250, 250))
        pygame.display.flip()
        alpha = alpha + 1
        if alpha == 255:
            alpha = 0


if __name__ == '__main__': main()
