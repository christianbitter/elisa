from elisa.game import Game, GameRenderer


class Pong(Game):
    def __init__(self, **kwargs):
        super().__init__(name='Extreme Pong', max_players=2, **kwargs)
        self._description = 'Extreme Pong is a clone of the well-known classic Pong.'

    def init(self, **kwargs) -> None:
        super().init(**kwargs)

    def start(self, **kwargs) -> None:
        super().start(**kwargs)

    def end(self, **kwargs) -> None:
        super().end(**kwargs)

    def shutdown(self, **kwargs):
        super().shutdown(**kwargs)

    def update(self):
        super().update()

    @property
    def finished(self):
        return super().finished()

    def __repr__(self):
        return super().__repr__()

    def get_render_state(self) -> dict:
        return super().get_render_state()


class PongRenderer(GameRenderer):
    def __init__(self):
        super().__init__()

    def render(self, buffer):
        return super().render(buffer)

    def set_game_state(self, state: dict) -> None:
        super().set_game_state(state)