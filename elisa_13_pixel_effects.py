# auth: christian bitter
# name: elisa_13_pixel_effects.py
# desc: we build on the elisa sprite example and apply some 2D image transforms/ filters
#       for some filters see
#       https://en.wikipedia.org/wiki/Kernel_(image_processing)
#       http://aishack.in/tutorials/image-convolution-examples/
#       http://machinelearninguru.com/computer_vision/basics/convolution/image_convolution_1.html

import pygame
from sprites import SpriteAssetManager


def clear_colour(px_surf: pygame.Surface, c: pygame.Color = pygame.Color(128, 192, 255, 255)):
    """
    for starters make all pixels the same colour in this highly inefficient manner
    :param px_surf: (Surface) Object representing the surface to be modified
    :param c: (pygame.Color) colour to set for each pixel in the PixelArray
    :return: Surface of modified PixelArray
    """
    if not px_surf:
        raise ValueError("surface not provided")

    px_array = pygame.PixelArray(px_surf)
    width, height = px_array.shape
    for iy in range(height):
        for ix in range(width):
            px_array[ix, iy] = c
    s = px_array.make_surface()
    px_array.close()
    return s


def lighten_colour(px_surf: pygame.Surface, colorkey: pygame.Color, lighten_val: int = 30):
    """
    lighten all pixels in the image
    :param px_surf: (Surface) Object representing the surface to be modified
    :param colorkey: (pygame.Color) colour key value ... pixels with colorkey color are not modified
    :param lighten_val: (int) value by how much colour is increased
    :return: Surface of modified PixelArray
    """
    if not px_surf:
        raise ValueError("surface not provided")

    px_array = pygame.PixelArray(px_surf)
    width, height = px_array.shape
    for iy in range(height):
        for ix in range(width):
            c_old = px_array.surface.get_at((ix, iy))
            # debug: print("c_old vs. ckey: {} vs. {}".format(c_old, colorkey))
            if c_old != colorkey:
                c_new = pygame.Color(min(255, c_old.r + lighten_val),
                                     min(255, c_old.g + lighten_val),
                                     min(255, c_old.b + lighten_val))
                px_array[ix, iy] = c_new
    s = px_array.make_surface()
    if colorkey is not None:
        s.set_colorkey(colorkey)
    px_array.close()
    return s


def darken_colour(px_surf: pygame.Surface, colorkey: pygame.Color, darken_val: int = 30):
    """
    darken all pixels in the image
    :param px_surf: (Surface) Object representing the surface to be modified
    :param colorkey: (pygame.Color) colour key value ... pixels with colorkey color are not modified
    :param darken_val: (int) value by how much colour is reduced
    :return: Surface of modified PixelArray
    """
    if not px_surf:
        raise ValueError("surface not provided")
    px_array = pygame.PixelArray(px_surf)
    width, height = px_array.shape
    for iy in range(height):
        for ix in range(width):
            c_old = px_array.surface.get_at((ix, iy))
            # debug: print("c_old vs. ckey: {} vs. {}".format(c_old, colorkey))
            if c_old != colorkey:
                c_new = pygame.Color(max(0, c_old.r - darken_val),
                                     max(0, c_old.g - darken_val),
                                     max(0, c_old.b - darken_val))
                px_array[ix, iy] = c_new
    s = px_array.make_surface()
    if colorkey is not None:
        s.set_colorkey(colorkey)
    px_array.close()
    return s


def filter_image(px_surf: pygame.Surface, colorkey: pygame.Color, filter_name: str = 'identity'):
    """
    Applies a filter (3x3 operator) to the provided surface
    :param px_surf: (Surface) Object representing the surface to be modified
    :param colorkey: (pygame.Color) colour key value ... pixels with colorkey color are not modified
    :param filter_name: name of filter to apply, can be any of the following identity, sharpen, blur, edge
    :return: Surface of modified PixelArray
    """
    if not px_surf:
        raise ValueError("surface not provided")

    px_array = pygame.PixelArray(px_surf)
    # notice that the sharpen and edge filters have some trouble with the image, since it is and upscaled
    # pixel art image, which contains some small almost non-visible noise.
    filter_zero = [[0, 0, 0],
                   [0, 0, 0],
                   [0, 0, 0]]
    filter_edge = [[-1, -1, -1],
                   [-1,  8, -1],
                   [-1, -1, -1]]
    filter_identity = [[0, 0, 0],
                       [0, 1, 0],
                       [0, 0, 0]]
    filter_sharpen = [[ 0, -1,  0],
                      [-1,  5, -1],
                      [ 0, -1,  0]]
    blr = 1./ 9.
    filter_blur = [[blr, blr, blr],
                   [blr, blr, blr],
                   [blr, blr, blr]]
    filter_mat = {
        'sharpen': filter_sharpen,
        'identity': filter_identity,
        'blur': filter_blur,
        'edge': filter_edge
    }.get(filter_name, filter_zero)

    k_h, k_w = 3, 3
    width, height = px_array.shape
    for iy in range(0, height):
        for ix in range(0, width):
            # any pixel outside of the image bounds, yields a 0 contribution
            # in that case we do not need to do anything
            accum_r, accum_g, accum_b = 0, 0, 0
            for yk in range(-1, k_h - 1):
                for xk in range(-1, k_w - 1):
                    iy_j, ix_j = iy + yk, ix + xk
                    ky_j, kx_j = yk + 1, xk + 1
                    k_val = filter_mat[ky_j][kx_j]
                    if 0 <= iy_j <= (height - 1) and 0 <= ix_j <= (width - 1):
                        c_old = px_array.surface.get_at((ix_j, iy_j))
                        i_old = px_array[ix_j, iy_j]
                        i_val_r, i_val_g, i_val_b = c_old[0], c_old.g, c_old.b
                        if i_old != 0 and k_val != 0:
                            accum_r += i_val_r * k_val
                            accum_g += i_val_g * k_val
                            accum_b += i_val_b * k_val

            c_new = pygame.Color(min(255, max(0, int(accum_r))),
                                 min(255, max(0, int(accum_g))),
                                 min(255, max(0, int(accum_b))),
                                 255)
            px_array[ix, iy] = c_new

    s = px_array.make_surface()
    if colorkey is not None:
        s.set_colorkey(colorkey)
    px_array.close()
    return s


def main():
    pygame.init()

    S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Elisa - Pixel Effects"
    C_WHITE = (255, 255, 255)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    # FPS watcher
    is_done = False

    # load a sprite map, and extract a particular sprite - idle_1 - from it
    am = SpriteAssetManager()
    sm_meta_json_fp = 'asset/elise_character/tileset_elisa_idle@8x.json'
    am.add_sprite_map(name='ELISA_IDLE', metadata_fp=sm_meta_json_fp, verbose=True)
    sprite_map = am['ELISA_IDLE']
    sprite_idle_1 = sprite_map['idle_1']
    img_elisa_idle = sprite_idle_1.image
    # set a colour key
    ck = pygame.Color(0, 0, 0, 0)
    img_elisa_idle.set_colorkey(ck)

    # apply our filters/ image operators
    pac_sprite = clear_colour(img_elisa_idle.copy(), pygame.Color(192, 128, 64, 255))
    pal_sprite = lighten_colour(img_elisa_idle.copy(), colorkey=ck)
    pad_sprite = darken_colour(img_elisa_idle.copy(), colorkey=ck)
    pad_edge   = filter_image(img_elisa_idle.copy(), colorkey=ck, filter_name='blur')

    # show the resulting images until we are done
    while not is_done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True

        back_buffer.blit(pac_sprite, (100, 100))

        back_buffer.blit(img_elisa_idle, (50, 100))
        back_buffer.blit(pal_sprite, (100, 100))
        back_buffer.blit(pad_sprite, (150, 100))
        back_buffer.blit(pad_edge,   (300, 100))

        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()
