# auth: christian bitter
# desc: this builds on elisa_1 by adding the animation through sprite sheet

import os
import sys
import pygame


def load_image(fp, colorkey=None, image_only=False):
    if not fp:
        raise ValueError("load_image - fp not provided")

    fullname = os.path.join(fp)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Cannot load image:", fp)
        raise SystemExit(message)

    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)

    if image_only:
        return image
    else:
        return image, image.get_rect()


def load_png(fp, image_only=False):
    """ Load image and return image object"""
    if not fp:
        raise ValueError("load_png - fp not provided")
    if not os.path.exists(fp):
        raise ValueError("load_png - {} does not exist".format(fp))

    fullname = os.path.join(fp)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print("Cannot load image:", fullname)
        raise SystemExit(message)
    if image_only:
        return image
    else:
        return image, image.get_rect()


class Elisa(pygame.sprite.Sprite):
    def __init__(self, asset_base_path, *groups):
        super().__init__(*groups)

        self.asset_base_path = asset_base_path
        self.gfx_width = 256
        self.gfx_height = 256
        self.animation_asset = {
            k: os.path.join(self.asset_base_path, v)
            for k, v in zip(["WALK"], ["elise_walk@8x.png"])
        }
        self.animation_tile = {}
        self.animation_sprite = {}
        self.animation_frame = {k: f for k, f in zip(["WALK"], [6])}
        self.animation_idx = {
            "WALK": [(0, 0), (256, 0), (512, 0), (768, 0), (1024, 0), (1280, 0)]
        }
        self.current_animation = None
        self.current_animation_frame = -1
        self.current_sprite = None

    def initialize(self):
        self.current_animation = "WALK"
        self.current_animation_frame = 0

        self.animation_tile = {
            k: load_png(fp, image_only=True) for k, fp in self.animation_asset.items()
        }

        for k, regions in self.animation_idx.items():
            v_surface = []
            for xmin, ymin in regions:
                anim_img = self.animation_tile[k]
                sprite = anim_img.subsurface(
                    xmin, ymin, self.gfx_width, self.gfx_height
                )
                v_surface.append(sprite)
            self.animation_sprite[k] = v_surface

        print(self.animation_sprite)

    def update(self):
        if not self.current_animation:
            raise ValueError("Call initialize first")
        if self.current_animation_frame == -1:
            raise ValueError("Call initialize first")
        if not self.animation_tile:
            raise ValueError("Call initialize first")
        if not self.animation_sprite:
            raise ValueError("Sprite Set not initialized")

        max_frames = self.animation_frame[self.current_animation]
        self.current_animation_frame += 1
        self.current_animation_frame = self.current_animation_frame % max_frames
        self.current_sprite = self.animation_sprite[self.current_animation][
            self.current_animation_frame
        ]


def main():
    if not pygame.font:
        print("Pygame - Font")
    if not pygame.mixer:
        print("Pygame - Mixer")

    pygame.init()
    elisa = Elisa("asset/elise_character/")

    is_done = False
    game_clock = pygame.time.Clock()

    S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Elisa2"
    C_WHITE = (250, 250, 250)

    front_buffer = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)

    back_buffer = pygame.Surface(front_buffer.get_size())
    back_buffer.fill(C_WHITE)

    elisa.initialize()

    while not is_done:
        game_clock.tick(25)

        elisa.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                is_done = True

        front_buffer.blit(back_buffer, (0, 0))
        front_buffer.blit(elisa.current_sprite, (100, 100))

        pygame.display.flip()


if __name__ == "__main__":
    main()
