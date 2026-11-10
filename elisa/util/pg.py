import pygame as pg

from elisa.linalg import Point2
from elisa.linalg.geom import Circle2


def pg_draw_circle(
    buffer: pg.Surface, circle: Circle2, color, lw: int = 1, show_center: bool = False
):
    if show_center:
        pg.draw.circle(
            buffer,
            color,
            (int(circle.center.x), int(circle.center.y)),
            2,
            0,
        )

    pg.draw.circle(
        buffer,
        color,
        (int(circle.center.x), int(circle.center.y)),
        int(circle.radius),
        lw,
    )


def pg_draw_line(buffer: pg.Surface, start: Point2, end: Point2, color, lw: int = 1):

    pg.draw.line(
        buffer,
        color,
        (int(start.x), int(start.y)),
        (int(end.x), int(end.y)),
        lw,
    )
