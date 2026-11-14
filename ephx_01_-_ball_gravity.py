# auth: christian bitter
# name: ephx_-_ball_gravity.py
# desc: a ball drops due to gravity. once it hits the floor we abort.
# vers: 0.1

from __future__ import annotations

import pygame

from elisa.linalg import Vec2
from elisa.physix import Body, World
from elisa.physix.constants import FIXED_DT, GRAVITY_Y

Y0 = 400.0  # release height in metres (y is measured up)
FLOOR_Y = 100.0  # floor height in metres
BALL_RADIUS = 10.0  # ball radius in pixels

C_BLUE = (0, 0, 255)
C_BLACK = (0, 0, 0)
C_GRAY = (128, 128, 128)


def render(screen: pygame.Surface, renderables: list) -> None:
    """Draw the ball at its current position."""
    # convert metres to pixels and flip y-axis for screen space
    screen.fill(C_BLACK)

    for renderable in renderables:
        renderable["render"](screen, renderable["obj"])


def render_ball(screen: pygame.Surface, body: Body) -> None:
    """Draw the ball at its current position."""
    # convert metres to pixels and flip y-axis for screen space
    x = int(body.position.x)
    y = int(screen.get_height() - body.position.y)
    pygame.draw.circle(screen, C_BLUE, (x, y), BALL_RADIUS)


def render_wall(screen: pygame.Surface, body: Body) -> None:
    """Draw the floor at its current position."""
    # convert metres to pixels and flip y-axis for screen space
    x = int(body.position.x)
    y = int(screen.get_height() - body.position.y)
    pygame.draw.rect(
        screen,
        color=C_GRAY,
        rect=(0, y, screen.get_width(), y + 10),
        width=1,
    )


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    pygame.init()

    w, h, t = 640, 480, "Elisa Physics - A dropping ball with gravity"
    c_white = (255, 255, 255)

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(c_white)

    world = World(dt=FIXED_DT, gravity=Vec2(0.0, GRAVITY_Y))
    ball = world.add(Body(position=Vec2(w // 2, Y0)))
    bottom = world.add(
        Body(position=Vec2(0, FLOOR_Y), inv_mass=0.0, is_static=True)
    )

    renderables = [
        {"id": 0, "obj": ball, "render": render_ball},
        {"id": 1, "obj": bottom, "render": render_wall},
    ]

    fps_watcher = pygame.time.Clock()
    is_done = False

    while not is_done:
        _ = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

        # advance physics and draw our ball
        world.step()

        render(back_buffer, renderables)

        if ball.position.y <= FLOOR_Y + BALL_RADIUS:
            is_done = True

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()


if __name__ == "__main__":
    main()
