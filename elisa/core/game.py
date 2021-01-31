from __future__ import annotations

from .player import Player


class Environment(object):
    """Defines a virtual environment, such as those used by games."""

    def __init__(self, name: str, **kwargs) -> None:
        super(Environment, self).__init__()
        self._name = name
        self._description = str(kwargs.get("description", None))
        self._action_space = {}
        self._state_space = {}

    @property
    def action_space(self) -> dict:
        return self._action_space

    @property
    def state_space(self) -> dict:
        return self._state_space

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description


class Game(Environment):
    """
    Base class of our games. This is a container for adding and removing players,
    as well as a pattern for initializing and finalizing state.
    """

    def __init__(self, name: str, max_players: int = 1, **kwargs):
        """Initialize a new game instance.

        Args:
            name (str): name of the string
            max_players (int, optional): Number of players for this game. Defaults to 1.
        """
        super(Game, self).__init__(name=name, **kwargs)
        self._running = False
        self._menu = None
        self._players = {}
        self._no_max_players = max_players

    def initialize(self, **kwargs) -> Game:
        """Provides an initialization point for our game.

        Returns:
            Game: the game instance
        """
        return self

    def start(self, **kwargs) -> Game:
        """Start the game, i.e. set running to True

        Returns:
            Game: The started game
        """
        self._running = True
        return self

    def end(self, **kwargs) -> Game:
        """End the game here, i.e. set running to False.

        Returns:
            Game: the ended game instance.
        """
        self._running = False
        return self

    def shutdown(self, **kwargs) -> Game:
        """Provides a finalization point for our game, i.e. call all shutdown logic here.

        Returns:
            Game: the cleaned game instance.
        """
        return self

    def update(self, time_delta: float, **kwargs) -> Game:
        """The update loop of our game.

        Args:
            time_delta (float): Time increment between the last call to update in order
            to derive the updates for game sub-systems.

        Returns:
            Game: the updated game instance
        """
        return self

    @property
    def finished(self):
        return False

    def add_player(self, p: Player) -> Game:
        """Add a new player to the game.

        Args:
            p (Player): Player to add

        Raises:
            ValueError: raised if the player or her id is not provided. raised if the max players is already reached.

        Returns:
            Game: the game instance with added player
        """
        if p is None:
            raise ValueError("Player not provided")

        p_id = str(p.id)

        if p_id is None or p_id.strip() == "":
            raise ValueError("Player id not provided")
        if p_id in self._players:
            raise ValueError("Player with id already added")
        if len(self._players) >= self._no_max_players:
            raise ValueError("Max Players already reached")

        self._players[p_id] = p
        return self

    def remove_player(self, player_id: str) -> Game:
        """Remove a player from the game.

        Args:
            player_id (str): id of player to remove from the game.

        Raises:
            ValueError: raised if the id is not provided or empty, if the id is not registered or the game does not have any player left.

        Returns:
            Game: the updated game.
        """
        if not player_id or player_id.strip == "":
            raise ValueError("Player id not provided")
        if player_id not in self._players:
            raise ValueError("Player id not in players")
        if len(self._players) < 1:
            raise ValueError("No player present")
        del self._players[player_id]
        return self

    def player_alive(self, name: str) -> bool:
        if name is None or name.strip() == "":
            raise ValueError("player name not provided")

        alive = [self._players[pid].name == name for pid in self._players]

        return any(alive)

    def __getitem__(self, i):
        if isinstance(i, int):
            # by index
            if i < 0 or i > len(self._players):
                raise KeyError("Index outside of the bounds of the players collection")
            for _jdx, pid in enumerate(self._players):
                if _jdx == i:
                    return self._players[pid]
            raise KeyError("Player at index not found")
        elif isinstance(i, str):
            return self._players[i]
        else:
            raise ValueError(
                "Unknown key type to retrieve players provide integer for position or str for id"
            )

    def player_names(self) -> list:
        return [self._players[pid].name for pid in self._players]

    @property
    def max_players(self):
        return self._no_max_players

    def __repr__(self) -> str:
        return "{}".format(self._name)

    def __str__(self) -> str:
        return self.__repr__()
