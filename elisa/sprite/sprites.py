import os
import pygame
import json
import uuid
from pygame import Surface, PixelArray
from uuid import uuid4

def load_image(fp, colorkey=None, image_only: bool = False, verbose: bool = False):
    if not fp:
        raise ValueError("load_image - fp not provided")

    fullname = os.path.join(fp)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', fp)
        raise SystemExit(message)

    if image.get_alpha() is None:
        if verbose:
            print("change the pixel format image to constant alpha or colorkey")
        image = image.convert()
    else:
        if verbose:
            print("change the pixel format image including per pixel alphas")
        image = image.convert_alpha()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        if verbose:
            print("Setting colour key: ", colorkey)
        image.set_colorkey(colorkey, pygame.RLEACCEL)

    if verbose:
        print("Loaded image: ", image)
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
        print('Cannot load image:', fullname)
        raise SystemExit(message)
    if image_only:
        return image
    else:
        return image, image.get_rect()