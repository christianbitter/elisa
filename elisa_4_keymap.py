# auth: christian bitter
# desc: in this tutorial we register key events and display some text accordingly
#       specifically, we are going to listen for the 4 arrow keys

import pygame
from pygame.locals import *

if not pygame.font: print("Pygame - fonts not loaded")
if not pygame.mixer: print("Pygame - audio not loaded")


def update_keytext(pressed, keymap):
    if not pressed: 
        return "None"
    txt = ""

    if keymap[K_UP]: txt += "UP"
    if keymap[K_DOWN]: txt += " DOWN"
    if keymap[K_LEFT]: txt += " LEFT"
    if keymap[K_RIGHT]: txt += " RIGHT"

    return txt.lstrip()


# init pygame - create the main window, and a background surface
pygame.init()

S_WIDTH = 640
S_HEIGHT= 480
S_TITLE = "PyBlocks"

C_WHITE = (250, 250, 250)
C_BLUE = (0, 0, 255)

screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
pygame.display.set_caption(S_TITLE)
pygame.mouse.set_visible(True)

back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
back_buffer = back_buffer.convert()
back_buffer.fill(C_WHITE)

# FPS watcher
fps_watcher = pygame.time.Clock()
is_done = False

# Display some text
font = pygame.font.Font(None, 36)
text = font.render("You pressed: <PLACEHOLDER>", 1, C_BLUE)
textpos = text.get_rect()
textpos.centerx = back_buffer.get_rect().centerx - 50
textpos.centery = back_buffer.get_rect().centery - 18

key_map = pygame.key.get_pressed()
pressed = False

while not is_done:
    fps_watcher.tick(60)

    for event in pygame.event.get():
        if event.type == QUIT:
            is_done = True
        else:
            pressed = event.type == pygame.KEYDOWN
            key_map = pygame.key.get_pressed()

    text = font.render("You pressed: {}".format(update_keytext(pressed, key_map)), 1, C_BLUE)
    back_buffer.fill(C_WHITE)
    back_buffer.blit(text, textpos)
    screen_buffer.blit(back_buffer, (0, 0))
    pygame.display.flip()
