# auth: christian bitter
# name: start_template_ephx
# vers: 0.1

import pygame

from elisa.linalg import Vec2
from elisa.linalg.geom import Circle2
from elisa.physix import Body, World

C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)


def render_circle(buffer: pygame.Surface, obj: Circle2) -> None:
    pygame.draw.circle(buffer, C_WHITE, obj.center, obj.radius)


def render(buffer: pygame.Surface, renderables: list) -> None:
    """Draw the ball at its current position."""
    # convert metres to pixels and flip y-axis for screen space
    buffer.fill(C_BLACK)

    for renderable in renderables:
        renderable["render"](buffer, renderable["obj"])


def update_body(renderables: list):
    for r in renderables:
        pi: Body = r["body"]
        r["obj"].set_xy(pi.position.x, pi.position.y)


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    pygame.init()

    w, h, t = 640, 480, "Elisa - <The Name of The Example>"
    fixed_dt = 1.0
    c_white = (255, 255, 255)

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(c_white)

    n = 50
    world = World(dt=fixed_dt, gravity=Vec2(0.0, 0.0))

    renderables = []

    for i in range(n):
        ci = Circle2.random(w, h, 10)
        bi = Body(
            position=ci.center,
            velocity=Vec2.random(),
            acceleration=Vec2.ZERO(),
            inv_mass=1.0,
            is_static=False,
        )
        renderables.append({"obj": ci, "render": render_circle, "body": bi})
        world.add(body=bi)

    fps_watcher = pygame.time.Clock()
    is_done = False

    while not is_done:
        _ = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

        world.step()

        # update the positions from body to renderables
        update_body(renderables)

        render(back_buffer, renderables)

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()


if __name__ == "__main__":
    main()
