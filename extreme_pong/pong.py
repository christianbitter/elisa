from elisa.game import Game, GameRenderer
from elisa.game import Player
from elisa.player import PlayerType
from pong_ui import OptionsScreen, MainScreen, GameScreen, AboutScreen


class PongPlayer(Player):
    def __init__(self, name: str, p_type: PlayerType, fp_pictogram: str):
        super().__init__(name, p_type)
        self._fp_pictogram = fp_pictogram
        self._pictogram = None
        self.__load_pictogram__()

    def __load_pictogram__(self):
        """
        TODO: __load_pictogram__
        :return:
        """
        pass

    @property
    def pictogram_path(self):
        return self._fp_pictogram

    @property
    def pictogram(self):
        return self._pictogram


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
    def __init__(self, sc_width, sc_height):
        super().__init__()
        self._main_screen = MainScreen(name='scMain', title='Extreme Pong', width=sc_width, height=sc_height)
        self._options_screen = OptionsScreen(name='scOptions', title="Options", width=sc_width, height=sc_height)
        self._game_screen = GameScreen(name='scGame', title="Game", width=sc_width, height=sc_height)
        self._about_screen = AboutScreen(name='scAbout', title="About", width=sc_width, height=sc_height)

        self.window_manager.add_screen([self._main_screen, self._options_screen, self._about_screen, self._game_screen])
        self.window_manager.active_screen = self._main_screen

    def render(self, buffer):
        return super().render(buffer)

    def set_game_state(self, state: dict) -> None:
        super().set_game_state(state)