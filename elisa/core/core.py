from enum import Enum


class PlayerType(Enum):
    """
    Enumeration of different player types.
    """

    CPU = 1
    Human = 2

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.__repr__()


class GameDifficulty(Enum):
    """
    enumeration defining game difficulty
    """

    EASY = 1
    MEDIUM = 2
    HARD = 3

    def __str__(self):
        return self.name
