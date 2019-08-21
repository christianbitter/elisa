from enum import Enum
from elisa.ui.ui import WindowManager
from .player import Player


class GameDifficulty(Enum):
    """
    enumeration defining game difficulty
    """

    EASY = 1
    MEDIUM = 2
    HARD = 3

    def __str__(self):
        return self.name


class Game(object):
    """
    Base class of our games
    """

    def __init__(self, name, max_players, **kwargs):
        """Constructor for Game"""
        super(Game, self).__init__()
        self._running = False
        self._menu = None
        self._name = name
        self._players = {}
        self._no_max_players = max_players
        if 'description' in kwargs: self._description = kwargs['description']

    def init(self, **kwargs) -> None:
        """
        initialization routines go here
        :return: None
        """
        pass

    def start(self, **kwargs) -> None:
        """
        The the game or a game round/ iteration
        :return: (None)
        """
        pass

    def end(self, **kwargs) -> None:
        """
        End the game or a game round/ iteration
        :return: (None)
        """
        pass

    def shutdown(self, **kwargs):
        """
        finalization routines and shutdown goes here
        :return:
        """
        pass

    def update(self):
        pass

    @property
    def finished(self):
        return False

    def add_player(self, p: Player):
        if p is None:
            raise ValueError("Player not provided")
        if p.id in self._players.keys():
            raise ValueError("Player with id already added")
        if len(self._players) >= self._no_max_players:
            raise ValueError("Max Players already reached")

        self._players[p.id] = p

    def remove_player(self, player_id: str):
        if not player_id:
            raise ValueError("Player id not provided")
        if player_id not in self._players.keys():
            raise ValueError("Player id not in players")
        if len(self._players) < 1:
            raise ValueError("No player present")
        _ = self._players.pop(player_id)

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def max_players(self):
        return self._no_max_players

    def __repr__(self):
        return "{}".format(self._name)

    def get_render_state(self) -> dict:
        """
        Provide all the state necessary to successfully render the game per time step
        :return: a dict with relevant key-value pairs
        """
        return {}


class GameRenderer(object):
    """"""

    def __init__(self, ):
        """Constructor for GameRenderer"""
        super(GameRenderer, self).__init__()
        self._game_state = None
        self._wm = WindowManager()

    @property
    def active_screen(self):
        return self._wm.active_screen

    @property
    def window_manager(self):
        return self._wm

    def render(self, buffer):
        raise ValueError("Not implemented")

    def set_game_state(self, state: dict) -> None:
        self._game_state = state
