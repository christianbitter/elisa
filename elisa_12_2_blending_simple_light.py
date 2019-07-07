# auth: christian bitter
# name: elisa_12_2_blending_simple_light.py
# desc: using alpha blending and a surface composed of differently alpha-saturated circles
#   - create light source
#   - load sprite character onto dark background
#   - enable pixel-perfect blending for light source surface
#   - show the lighting texture where the mouse is
#   - blend texture correctly - additive brightens everything where the blending occurs

import pygame
from sprites import SpriteAssetManager


def create_light(light_color, radius: int = 50):
    """
    create a circular fake light source of specific light colour. this amounts to an alpha-blendable
    circle, that brightens the colour of the underlying source surface if blend mode add is used
    :param light_color: 4 tuple defining the light colour
    :param radius: radius of the light source
    :return: a surface that should be blitted with pygame.BLEND_ADD, BLEND_RGB_ADD or BLEND_RGBA_ADD in order to create
    the intended lighting effect.
    """
    if radius < 1:
        raise ValueError("Radius < 1")
    l_r = radius
    l_c = max(1, int(.05 * radius))  # core is 10% of the full light circle

    # create a per-pixel alpha surface into which we draw the light source
    s1 = pygame.Surface((2*l_r, 2*l_r), pygame.SRCALPHA)  # per-pixel alpha
    # determine the inner white source
    pygame.draw.circle(s1, (255, 255, 255, 255), (l_r, l_r), l_c, l_c)
    # compute the r,g,b,a decrements across the possible range [0, colour]
    # and draw a circle with the respectively decremented colour of width r_inc
    # into the surface
    a_max, a_min = 255, 0
    r_max, r_min = light_color[0], 0
    g_max, g_min = light_color[1], 0
    b_max, b_min = light_color[2], 0
    a_inc = (a_max - a_min) / (l_r - (l_c + 1))
    r_inc = (r_max - r_min) / (l_r - (l_c + 1))
    g_inc = (g_max - g_min) / (l_r - (l_c + 1))
    b_inc = (b_max - b_min) / (l_r - (l_c + 1))
    a, r, g, b = a_max, r_max, g_max, b_max
    radius_inc = max(1, (radius - l_c) / (a_max - a_min))

    for x in range(l_c + 1, l_r, radius_inc):
        pygame.draw.circle(s1, (max(r, 0), max(g, 0), max(b, 0), max(a, 0)), (l_r, l_r), x, radius_inc)
        a -= a_inc
        r -= r_inc
        g -= g_inc
        b -= b_inc

    return s1


def main():
    # init pygame - create the main window, and a background surface
    pygame.init()

    S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Elisa 12-2 - Blending of generated surface onto elisa sprite"
    C_BLACK = (0, 0, 0)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size(), pygame.SRCALPHA)
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_BLACK)

    sam = SpriteAssetManager()
    sam.add_sprite_map(name='Elisa_Idle', metadata_fp='asset/elise_character/tileset_elisa_idle@8x.json')

    elisa_sprite = sam['Elisa_Idle']['idle_1']

    e_img    = elisa_sprite.image.convert()
    e_img.set_colorkey((255, 255, 255))
    e_img.set_alpha(255)

    s0 = pygame.Surface((elisa_sprite.width, elisa_sprite.height))  # per-pixel alpha
    s0.set_alpha(255)
    s0.blit(e_img, (0, 0))

    l_r = 50
    s1 = create_light((255, 0, 0), radius=l_r)

    is_done = False

    while not is_done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            else:
                pass

        l_x, l_y = x - l_r, y - l_r  # the coordinates of the light
        back_buffer.fill(C_BLACK)
        back_buffer.blit(s0, (100, 100))
        back_buffer.blit(s1, (l_x, l_y), special_flags=pygame.BLEND_ADD)

        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()
