# name: elisa_0_1_drawing_shapes.py
# auth: (c) 2020 christian bitter
# desc: foray into graphics and physics
# draw simple shapes - circle and rect. when the rect collides with the circle, mark it

from math import cos, pi, sin

import pygame as pg

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_BLUE = (0, 0, 255)
C_RED = (255, 0, 0)
ALPHA_2_RAD = 2.0 * pi / 360.0
S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Elisa - 0.1 Geoms"


def box_vs_box(box1, box2) -> bool:
    a1x, a1y, aw, ah = box1
    a2x, a2y = a1x + aw, a1y + ah

    b1x, b1y, bw, bh = box2
    b2x, b2y = b1x + bw, b1y + bh

    if a1x >= b1x and a1x <= b2x and a1y >= b1y and a1y <= b2y:
        return True

    if a2x >= b1x and a2x <= b2x and a1y >= b1y and a1y <= b2y:
        return True
    
    if a2x >= b1x and a2x <= b2x and a2y >= b1y and a2y <= b2y:
        return True

    if a1x >= b1x and a1x <= b2x and a2y >= b1y and a2y <= b2y:
        return True

    # the above check contained inside
    # but fail if we cover over the box

    return False


def collides(b0, b1, wx, wy, ww, wh):
    x0, y0 = b0
    x1, y1 = b1

    if wx > x1:
        return False

    m = (y1 - y0) / (x1 - x0)
    yi = (wx - x0) * m + y0

    # print(f"{m} - {yi} / {wx}, {wy}, {ww}, {wh}")
    return yi >= wy and yi <= wy + wh


# note: the orientation of the coordinate system is x-axis down - quadrant 4 is here number 1
def draw(
    buffer,
    wall_x: int,
    wall_y: int,
    w_2: int,
    h_2: int,
    bx: int,
    by: int,
    r: int,
    ball_alpha: int,
):
    buffer.fill(C_BLACK)

    pg.draw.circle(buffer, C_WHITE, center=(bx, by), radius=r, width=1)

    for a in [0, 15, 30, 45, 60, 75, 90]:
        # 2 * pi / 360 = x / alpha =>  alpha * 2 * pi / 360 = x
        alpha = a * ALPHA_2_RAD
        p1 = (bx + r * cos(alpha), by - r * sin(alpha))
        pg.draw.line(buffer, C_WHITE, (bx, by), p1, 1)

    p2 = bx + 2 * r * cos(ball_alpha), by - 2 * r * sin(ball_alpha)

    b0 = (bx, by)
    b1 = (
        bx + r * cos(ball_alpha * ALPHA_2_RAD),
        by - r * sin(ball_alpha * ALPHA_2_RAD),
    )
    b2 = (bx + r * cos(45 * ALPHA_2_RAD), by - r * sin(45 * ALPHA_2_RAD))
    b3 = (bx + r * cos(315 * ALPHA_2_RAD), by - r * sin(315 * ALPHA_2_RAD))

    pg.draw.line(buffer, C_RED, (bx, by), p2, 1)

    pg.draw.line(buffer, C_RED, (bx, by), b1, 1)
    pg.draw.line(buffer, C_RED, (bx, by), b2, 1)
    pg.draw.line(buffer, C_RED, (bx, by), b3, 1)

    wx, wy, ww, wh = wall_x - w_2, wall_y - h_2, w_2 * 2, h_2 * 2
    print(f"ball0: {b0}; ball1: {b1} - wall: {wx}, {wy}, {ww}, {wh}")

    bb = (bx - r, by - r, 2 * r, 2 * r)
    pb = (wall_x - w_2, wall_y - h_2, 2 * w_2, 2 * h_2)

    pg.draw.rect(buffer, C_WHITE, bb, width=1)

    fill = 1 - box_vs_box(pb, bb)
    pg.draw.rect(buffer, C_BLUE, pb, width=fill)


def main():
    np, nf = pg.init()
    print(f"Initialization: Pass = {np}, Fail = {nf}")

    screen_buffer = pg.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pg.display.set_caption(S_TITLE)
    pg.mouse.set_visible(True)

    back_buffer: pg.Surface = pg.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()

    fps_watcher = pg.time.Clock()
    is_done = False

    wall_x, wall_y, w_2, h_2 = 500, S_HEIGHT // 2, 25, 100
    b_x, b_y, r, ball_alpha = 100, 100, 50, 0

    while not is_done:
        _ = fps_watcher.tick(60)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_done = True
                break

        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            wall_x -= 1
        if keys[pg.K_RIGHT]:
            wall_x += 1
        if keys[pg.K_UP]:
            wall_y -= 1
        if keys[pg.K_DOWN]:
            wall_y += 1

        draw(
            buffer=back_buffer,
            wall_x=wall_x,
            wall_y=wall_y,
            w_2=w_2,
            h_2=h_2,
            bx=b_x,
            by=b_y,
            r=r,
            ball_alpha=ball_alpha,
        )

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
