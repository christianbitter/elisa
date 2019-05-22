import os, sys
import pygame
from pygame import locals

if not pygame.font: print("Pygame - fonts not loaded")
if not pygame.mixer: print("Pygame - audio not loaded")

# init pygame - create the main window, and a background surface

pygame.init()

S_WIDTH = 640
S_HEIGHT= 480
S_TITLE = "PyBlocks"

screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
pygame.display.set_caption(S_TITLE)
pygame.mouse.set_visible(True)

back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
back_buffer = back_buffer.convert()
back_buffer.fill((250, 250, 250))

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

    screen_buffer.blit(back_buffer, (0, 0))
    pygame.display.flip()