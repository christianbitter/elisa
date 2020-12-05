# auth: christian bitter
# desc: in this tutorial we register key events and display some text accordingly
#       specifically, we are going to listen for the 4 arrow keys

import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_DOWN, K_UP, QUIT

if not pygame.font:
    print("Pygame - fonts not loaded")
if not pygame.mixer:
    print("Pygame - audio not loaded")


def update_keytext(pressed, keymap):
    if not pressed:
        return "None"
    txt = ""

    if keymap[K_UP]:
        txt += "UP"
    if keymap[K_DOWN]:
        txt += " DOWN"
    if keymap[K_LEFT]:
        txt += " LEFT"
    if keymap[K_RIGHT]:
        txt += " RIGHT"

    return txt.lstrip()


# init pygame - create the main window, and a background surface
pygame.init()

w, h, t = 640, 480, "Elisa 4 - key map and input handling"

c_white = (250, 250, 250)
c_blue = (0, 0, 255)

screen_buffer = pygame.display.set_mode(size=(w, h))
pygame.display.set_caption(t)
pygame.mouse.set_visible(True)

back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
back_buffer = back_buffer.convert()
back_buffer.fill(c_white)

# FPS watcher
fps_watcher = pygame.time.Clock()
is_done = False

# Display some text
font = pygame.font.Font(None, 36)
text = font.render("You pressed: <PLACEHOLDER>", 1, c_blue)
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

    text_help = font.render("Press any of the arrow keys ...", 1, c_blue)
    text = font.render(
        "You pressed: {}".format(update_keytext(pressed, key_map)), 1, c_blue
    )

    back_buffer.fill(c_white)
    back_buffer.blit(text_help, (100, 100))
    back_buffer.blit(text, (100, 150))
    screen_buffer.blit(back_buffer, (0, 0))
    pygame.display.flip()
