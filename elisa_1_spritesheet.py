# auth: christian bitter
# desc: starting from the pygame introduction with a simple template.
#       this will not do much, other than create a window
#       and load a sprite sheet

import os
import pygame

if not pygame.font: print("Pygame - Font not loaded")
if not pygame.mixer: print("Pygame - Mixer not loaded")

def load_image(fp, colorkey=None):
    if not fp:
        raise ValueError("load_image - fp not provided")

    fullname = os.path.join(fp)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()

class Elisa(pygame.sprite.Sprite):
    def __init__(self, asset_base:str, *groups):
        super().__init__(*groups)
        self.asset_base_dir = asset_base

        self.animation_assets = {"IDLE": os.path.join(self.asset_base_dir, "elise_gun_walk@8x.png")}
        self.image, self.rect = load_image(self.animation_assets["IDLE"], -1)
        self.idle = 0

pygame.init()

fps_watcher = pygame.time.Clock()

S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Elisa1"
C_WHITE = (250, 250, 250)

screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
pygame.display.set_caption(S_TITLE)

back_buffer = pygame.Surface(screen_buffer.get_size())
back_buffer.fill(C_WHITE)

elisa = Elisa(asset_base="asset/elise_character")
allsprites = pygame.sprite.RenderPlain(elisa)
is_done = False

while not is_done:
    fps_watcher.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            is_done = True

    screen_buffer.blit(back_buffer, (0, 0))
    allsprites.draw(screen_buffer)
    pygame.display.flip()