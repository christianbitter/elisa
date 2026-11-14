import logging
import math
from abc import ABC

import pygame as pg

from elisa.linalg.geom import Circle2, Rect2
from elisa.linalg.intersection import intersects_AABB2
from elisa.sprite import SpriteSheet

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

C_BLACK = (0, 0, 0)
C_RED = (255, 0, 0)
C_BLUE = (0, 0, 255)
C_WHITE = (255, 255, 255)
C_GRAY = (128, 128, 128)

SCORE_LIMIT = 10

# TODO: hit and reflect of ball, requires direction vector at ball for refined hit test, and reflect at surface
# TODO: load sprite map and change player, ball sprite

# TODO: support in game items and one concrete item - point increase

# TODO: reset on point one
# TODO: game won on player reaches max points
# TODO: add a main screen with a menu for game, options and high score table


class Pong:
    def __init__(
        self, w: int = 640, h: int = 480, player_one: str = "P1", player_two: str = "P2"
    ):
        np, nf = pg.init()
        logger.info(f"Initialization: Pass = {np}, Fail = {nf}")

        self.player1_name = player_one
        self.player2_name = player_two

        self.players = {}
        self.subjects = []
        self.renderables = []

        self._bounds = (100, 100, 400, 400)
        self._left_bound = self._bounds[0]
        self._top_bound = self._bounds[1]
        self._right_bound = self._bounds[2]
        self._bottom_bound = self._bounds[3]

        self.screen_width = w
        self.screen_height = h

        self.setup_pygame()
        self._score = (0, 0)
        self.is_done = False

    def setup_ball(self):
        r = 10
        self._ball = Ball(
            x=self._left_bound + (self._right_bound - self._left_bound) // 2,
            y=self._bottom_bound + (self._bottom_bound - self._top_bound) // 2,
            r=r,
            sprite=self.gfx["ball"].as_pygame_sprite,
        )

        self.subjects.extend([self._ball])
        self.renderables.extend([self._ball])

    def setup_arena(self):
        wall_width = self._right_bound - self._left_bound
        wall_height = self._bottom_bound - self._top_bound
        wall_thickness = 10

        self._wall_east = Wall(
            self._right_bound, self._top_bound, wall_thickness, wall_height
        )
        self._wall_bottom = Wall(
            self._left_bound, self._bottom_bound, wall_width, wall_thickness
        )
        self._wall_west = Wall(
            self._left_bound - wall_thickness,
            self._top_bound,
            wall_thickness,
            wall_height,
        )
        self._wall_top = Wall(
            self._left_bound,
            self._top_bound - wall_thickness,
            wall_width,
            wall_thickness,
        )
        self.renderables.extend(
            [
                self._wall_east,
                self._wall_bottom,
                self._wall_west,
                self._wall_top,
            ]
        )

    def setup_players(self):
        if self.players.get("P1") and self.players.get("P2"):
            return

        paddle_width, paddle_height = 10, 100
        area_h = self._bottom_bound - self._top_bound

        p1 = Player(
            self.player1_name,
            self._left_bound,
            self._top_bound + (area_h - paddle_height) // 2,
            paddle_width,
            paddle_height,
            self.gfx["paddle_1"].as_pygame_sprite,
        )
        p2 = Player(
            self.player2_name,
            self._right_bound - paddle_width,
            self._top_bound + (area_h - paddle_height) // 2,
            paddle_width,
            paddle_height,
            self.gfx["paddle_2"].as_pygame_sprite,
        )

        self.players = {"P1": p1, "P2": p2}
        self.subjects.extend([p1, p2])
        self.renderables.extend([p1, p2])

    def setup_pygame(self):
        self.screen_buffer = pg.display.set_mode(
            size=(self.screen_width, self.screen_height)
        )
        pg.display.set_caption("Pong")
        pg.mouse.set_visible(True)

        self.back_buffer: pg.Surface = pg.Surface(self.screen_buffer.get_size())
        self.back_buffer = self.back_buffer.convert()

        self.game_font = pg.font.SysFont(None, 48)

        self.fps_watcher = pg.time.Clock()

    def load_assets(self):
        # TODO: prepare the real sprite map - background white
        # location and dimensions correct.
        # animation phases.
        sprite_map = {
            "name": "pong_sprite_map",
            "width": 1024,
            "height": 1024,
            "color_key": (255, 255, 255),
            "no_sprites": 3,
            "image_path": "asset/gfx/pong_sprite_map.png",
            "sprites": [
                {"name": "paddle_1", "x": 10, "y": 10, "width": 128, "height": 128},
                {"name": "paddle_2", "x": 10, "y": 10, "width": 128, "height": 128},
                {"name": "ball", "x": 10, "y": 10, "width": 128, "height": 128},
            ],
        }

        self.gfx = SpriteSheet().initialize_from_spritemap(sprite_map)

    def quit(self):
        pg.quit()

    @property
    def player1(self):
        return self.players.get("P1", None)

    @property
    def player2(self):
        return self.players.get("P2", None)

    def update(self, dt: float):
        for o in self.subjects:
            o.update(dt)

    def start(self):
        new_round, end_game, scorer = False, False, None
        # TODO: measure the time increment
        dt = 0.0

        while not self.is_done:
            dt = self.fps_watcher.tick(60)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.is_done = True
                    break

            self.update(dt)

            self.render(self.back_buffer)

            keys = pg.key.get_pressed()

            # TODO: this goes into events - on_key
            # player one
            if keys[pg.K_w]:
                self.players["P1"].move_up()

            if keys[pg.K_s]:
                self.players["P1"].move_down()

            # player two
            if keys[pg.K_UP]:
                self.players["P2"].move_up()

            if keys[pg.K_DOWN]:
                self.players["P2"].move_down()

            s1, s2 = self._score

            new_round, end_game, scorer = False, False, None

            if intersects_AABB2(self._ball.AABB, self.player1.AABB):
                raise ValueError("reflect ball <-> player 1")
                continue
            elif intersects_AABB2(self._ball.AABB, self.player2.AABB):
                raise ValueError("reflect ball <-> player 2")
                continue
            if intersects_AABB2(self._ball.AABB, self._wall_east.AABB):
                s2 += 1
                new_round = True
                end_game = s2 > SCORE_LIMIT
                scorer = "P2"
                raise ValueError("intersects_AABB2(self._ball.AABB, self._wall_east)")

            elif intersects_AABB2(self._ball.AABB, self._wall_west.AABB):
                s1 += 1
                new_round = True
                end_game = s1 > SCORE_LIMIT
                scorer = "P1"
                raise ValueError("intersects_AABB2(self._ball.AABB, self._wall_east)")

            # TODO: check new round due to score or end due to win
            if end_game:
                logger.info(f"End Game - Player {self.players[scorer].name} won")

            if new_round:
                logger.info(f"New Round - Player {self.players[scorer].name} scored")

            if not self.is_done:
                self.screen_buffer.blit(self.back_buffer, (0, 0))
                pg.display.flip()

    @property
    def score(self):
        return self._score

    @property
    def score_text(self) -> str:
        return f"{self._score[0]} : {self._score[1]}"

    def render_hud(self, s: pg.Surface):
        if not "P1" in self.players and not "P2" in self.players:
            return 

        F_GAME = self.game_font

        t_p1 = F_GAME.render(self.players["P1"].name, True, C_RED)
        t_p2 = F_GAME.render(self.players["P2"].name, True, C_BLUE)
        t_score = F_GAME.render(self.score_text, True, C_WHITE)

        s.blit(t_p1, (self._left_bound, self._top_bound // 2))
        s.blit(t_p2, (self._right_bound, self._top_bound // 2))
        s.blit(t_score, (250, self._top_bound // 2))

    def clear_screen(self, s: pg.Surface):
        s.fill(C_BLACK, (0, 0, self.screen_width, self.screen_height))

    def render_renderables(self, s: pg.Surface):
        for r in self.renderables:
            r.draw(s)

    def render(self, s):
        self.clear_screen(s)
        self.render_hud(s)
        self.render_renderables(s)


class GameObject(ABC):
    def __init__(self, x: float, y: float, actor_type: str):
        super().__init__()
        self.actor_type = actor_type
        self._pos = (x, y)
        self.x = x
        self.y = y
        self._angle = 0.0
        self._velocity = 0.0
        self._acceleration = 0.0
        self._geom = None

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    def set_pos(self, value):
        self._pos = value

    def hit(self, other) -> bool:
        return False

    def update(self, dt: float):
        pass

    def draw(self, s: pg.Surface):
        pass

    def AABB(self) -> Rect2:
        raise ValueError("Not Implemented")

    def set_x(self, x: int):
        self.x = x

    def set_y(self, y: int):
        self.y = y


class Wall(GameObject):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, "ImmovableObject")

        self.width = w
        self.height = h
        self._geom = Rect2(
            (x, y),
            (x + w, y),
            (x + w, y + h),
            (x, y + h),
        )
        self._aabb = Rect2((x, y), (x + w, y), (x + w, y + h), (x, y + h))

    def draw(self, s: pg.Surface):
        pg.draw.rect(
            s,
            C_GRAY,
            (self.x, self.y, self.width, self.height),
            0,  # filled
        )

    @property
    def AABB(self):
        return self._aabb


class Ball(GameObject):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        r: int = 10,
        angle: int = 0,
        velocity: float = 70.0,
        acceleration=0.0,
        sprite=None,
    ):
        super().__init__(x, y, "Object")

        self.r = r
        self._sprite = sprite
        self._geom = Circle2(p=(x, y), radius=r)
        self._velocity = velocity  # m/ s
        self._acceleration = acceleration  # m/ s^2
        self._aabb = Rect2(
            p0=(x - r, y - r), p1=(x + r, y - r), p2=(x + r, y + r), p3=(x - r, y + r)
        )

    def update(self, dt):
        delta_t = dt * 0.001
        dx = (
            delta_t * self._velocity + delta_t * delta_t * self._acceleration
        ) * math.cos(self._angle)
        dy = (
            delta_t * self._velocity + delta_t * delta_t * self._acceleration
        ) * math.sin(self._angle)

        self.x += dx
        self.y += dy

        for i in range(len(self._aabb.points)):
            self._aabb[i].x += dx
            self._aabb[i].y += dy

    @property
    def AABB(self):
        return self._aabb

    def hit(self, other):
        return False

    def draw(self, s):
        if self._sprite:
            s.blit(
                self._sprite,
                (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r),
            )
        else:
            pg.draw.circle(s, C_WHITE, (self.x, self.y), self.r, 1)


class Player(GameObject):
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        paddle_width: int = 10,
        paddle_height: int = 100,
        sprite=None,
    ):
        super().__init__(x, y, "Subject")
        self.name = name
        self.paddle_speed = 10
        self.paddle_width = paddle_width
        self.paddle_height = paddle_height
        self._direction = 0
        self._sprite = sprite
        self._geom = Rect2(
            (x, y),
            (x + paddle_width, y),
            (x + paddle_width, y + paddle_height),
            (x, y + paddle_height),
        )
        self._aabb = Rect2(
            (x, y),
            (x + paddle_width, y),
            (x + paddle_width, y + paddle_height),
            (x, y + paddle_height),
        )

    def draw(self, s: pg.Surface):
        if self._sprite:
            s.blit(
                source=self._sprite,
                dest=(self.x, self.y, self.paddle_width, self.paddle_height),
            )
        else:
            pg.draw.rect(
                s,
                C_RED,
                (self.x, self.y, self.paddle_width, self.paddle_height),
                0,  # filled
            )

    def set_y(self, y):
        self.y = y
        self._pos = (self.x, self.y)

        self._aabb.points[0].y = y
        self._aabb.points[1].y = y
        self._aabb.points[2].y = y + self.paddle_height
        self._aabb.points[3].y = y + self.paddle_height

    def move_down(self):
        self.set_y(self.y + self.paddle_speed)

    def move_up(self):
        self.set_y(self.y - self.paddle_speed)

    def update(self, dt: float):
        pass

    @property
    def AABB(self):
        return self._aabb


def main():
    logger.info("arcanoid")

    pong = Pong()

    pong.load_assets()
    pong.setup_players()
    pong.setup_arena()
    pong.setup_ball()

    pong.start()

    pong.quit()


if __name__ == "__main__":
    main()
