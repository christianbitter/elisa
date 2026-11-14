# name: elisa_0_1_drawing_circles.py
# auth: (c) 2026 christian bitter
# desc: moving circles, testing circle to circle intersection

import math

import pygame as pg

from elisa import Point2
from elisa.linalg.geom import Circle2
from elisa.physix.collision import circle_circle
from elisa.util import pg_draw_circle, pg_draw_line

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_BLUE = (0, 0, 255)
C_LIGHTBLUE = (128, 128, 255)
C_PURPLE = (128, 0, 255)
C_RED = (255, 0, 0)
C_GREEN = (0, 255, 0)
C_GRAY = (128, 128, 128)


def color_circles(c1, c2) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    d12 = (c2.center - c1.center).length
    r12 = c1.radius + c2.radius

    if math.isclose(d12, r12):
        # intersection in one point, touch, no overlap
        return C_RED, C_RED
    elif d12 < r12:
        # overlap - possibly one, 2 or zero touch
        if d12 >= c1.radius:
            return C_BLUE, C_BLUE
        elif math.isclose(d12 + c2.radius, c1.radius):
            return C_PURPLE, C_PURPLE
        else:
            return C_LIGHTBLUE, C_LIGHTBLUE
    elif d12 > c1.radius + c2.radius:
        # no touch, no intersection
        return C_WHITE, C_WHITE
    elif math.isclose(d12, 0) and math.isclose(c1.radius, c2.radius):
        # concentric, equal
        return C_GRAY, C_GRAY
    else:
        return C_GREEN, C_GREEN


def draw(buffer, circles: list[Circle2]):
    buffer.fill(C_BLACK)

    # we draw different circles with different colors and positions
    j = 0
    for i in range(len(circles) // 2):
        c1 = circles[j]
        c2 = circles[j + 1]

        d12 = c2.center - c1.center

        c1_color, c2_color = color_circles(c1, c2)

        pg_draw_circle(buffer, c1, c1_color, lw=1, show_center=True)
        pg_draw_circle(buffer, c2, c2_color, lw=1, show_center=True)
        pg_draw_line(buffer, c1.center, c1.center + d12, C_GREEN, lw=1)

        # visualize intersection points if any
        manif = circle_circle(c1, c2)
        if manif:
            for p in manif.contact:
                pg.draw.circle(buffer, (128, 64, 255), (p.x, p.y), radius=4, width=0)

        j += 2


def main():
    np, nf = pg.init()
    print(f"Initialization: Pass = {np}, Fail = {nf}")

    w, h, t = 640, 480, "Elisa - 0.1 Drawing Shapes"

    screen_buffer = pg.display.set_mode(size=(w, h))
    pg.display.set_caption(t)
    pg.mouse.set_visible(True)

    back_buffer: pg.Surface = pg.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()

    fps_watcher = pg.time.Clock()
    is_done = False

    circles = [
        Circle2(Point2(100.0, 100.0), 50.0),
        Circle2(Point2(200.0, 100.0), 50.0),
        Circle2(Point2(100.0, 250.0), 50.0),
        Circle2(Point2(200.0, 250.0), 25.0),
        Circle2(Point2(400.0, 100.0), 50.0),
        Circle2(Point2(450.0, 100.0), 50.0),
        Circle2(Point2(400.0, 250.0), 75.0),
        Circle2(Point2(450.0, 250.0), 25.0),
        Circle2(Point2(250.0, 400.0), 75.0),
        Circle2(Point2(275.0, 400.0), 25.0),
        # now add two more complicated ones
        Circle2(Point2(450.0, 400.0), 75.0),
        Circle2(Point2(550.0, 350.0), 30.0),
    ]

    dx = 0.5
    x = 0.0

    while not is_done:
        _ = fps_watcher.tick(30)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_done = True
                break

        # move all odd circles left and right
        x = x + dx
        if abs(x) > 50.0:
            dx = -dx

        for i, c in enumerate(circles):
            if i % 2 == 1:
                cx_i = c.center_x + dx
                c.set_xy(cx_i, c.center_y)

        draw(back_buffer, circles)

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
