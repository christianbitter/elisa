# auth: christian bitter
# vers: 0.1
# This is a simple game, where the player has to guess a randomly generated integer number. This number has to be
# in some range [0, MAX]. The player is given some x amount of tries to guess the number

# TODO: the game will issue some informative, conversational messages to keep the player engaged
# TODO: with each passed try, the goblin from the used art work will come closer to a peasant. Once all tries are out
#       the goblin will lay down - die!
# TODO: in a more difficult setting, the player has only some amount of seconds, before the clock ticks off
# TODO: the screen interface needs to be improved
# TODO: except for the main playing screen, all screens feature a simple calm background music
# A simple game menu, including ...
#  (start) new game
#  options
#   player name
#   set difficulty
#  view high score
    # TODO: a simple (high score) table UI element
#  view about ... this shows a simple description of the game, copyright message, version information and credits
    # TODO: introduce version
    # TODO: UI element multi-line label
#   Quit
#       Quits the game.
# menu items is shown.
# TODO: main screen shows the menu, in the background we see numbers moving, scaling and rotating
#           the numbers fade in and out of visibility in the background
#           TODO: 2d image transform - scale
#           TODO: 2d image transform - rotate
#           TODO: 2d image transform - translate
# TODO: all screen declarations go into the game renderer
# TODO: a game renderer has at least one active screen - the one where the game is rendered
# A simple high score mechanism including persistence is realized. Initially, the score directly mimics the number of
# tries used to finish a round. Only if the player succeeds will she be awarded a score.

import os
import csv
import uuid
import random
import pygame
from pygame.locals import *
from enum import Enum
from ui import Screen, UIEvent, Menu, MenuItem, FontStyle, Label, VerticalAlignment, WindowManager


class PlayerType(Enum):
    CPU = 1
    Human = 2


class Player(object):
    """"""

    def __init__(self, name, p_type: PlayerType):
        """Constructor for Player"""
        super(Player, self).__init__()
        self._name = name
        self._type = p_type
        self._id = uuid.uuid4()

    def __str__(self):
        return "[{}] {}".format(self._id, self._name)


    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def player_type(self):
        return self._type


class Game(object):
    """"""

    def __init__(self, name, max_players, **kwargs):
        """Constructor for Game"""
        super(Game, self).__init__()
        self._menu = None
        self._name = name
        self._players = {}
        self._no_max_players = max_players
        if 'description' in kwargs: self._description = kwargs['description']

    def init(self):
        pass

    def update(self):
        pass

    @property
    def finished(self):
        return False

    def add_player(self, p: Player):
        if not p:
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
    def desription(self):
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


class GuessMyNumber(Game):
    """"""

    def __init__(self, MAX_NUMBER=50, MAX_TRIES=10):
        """Constructor for GuessTheNumber"""
        super(GuessMyNumber, self).__init__(name='GuessTheNumber', max_players=1,
                                             description='A simple guess the number game')
        self._random_number = None
        self._max_number = MAX_NUMBER
        self._max_tries  = MAX_TRIES
        self._no_tries = 0
        self._digit_buffer = []
        self._is_finished = False
        self._player_has_won = False
        self._guess = None
        self._highscore = []
        self._score = None
        self._active_player = None
        self._score_table_fp = "guess_a_number_scores.csv"

    def init(self):
        self._random_number = random.randint(0, self._max_number)
        self._score  = 0
        self._active_player = [v for _, v in self._players.items()][0]
        self.load_scores()
        print("You have to guess: ", self._random_number)

    def update(self):
        # print("Player guesses: {}/ {}", self._guess, self._random_number)
        n = self._guess

        if n == self._random_number:
            self._player_has_won = True
            self._is_finished = self._player_has_won
            self._guess = None
            self._score = self._max_tries - self._no_tries
            self._highscore.append((self._active_player.name, self._score))
        else:
            self._is_finished = self._no_tries >= self._max_tries

    @property
    def player_has_won(self):
        return self._player_has_won

    @property
    def score(self):
        return self._score

    @property
    def finished(self):
        return self._is_finished

    @property
    def current_number(self):
        return "".join([str(d) for d in self._digit_buffer])

    @property
    def no_tries(self):
        return self._no_tries

    def close_call(self):
        yield "You are getting closer"

    def far_off(self):
        yield "Not really"

    @property
    def max_tries(self):
        return self._max_tries

    def commit_number(self):
        if len(self.current_number):
            self._no_tries += 1
            self._guess = int(self.current_number)
            self._digit_buffer = []

    def add_digit(self, d):
        self._digit_buffer.append(d)

    def load_scores(self):
        """
        load the high score table from the respective csv
        :return:
        """
        if self._score_table_fp and os.path.exists(self._score_table_fp):
            with open(self._score_table_fp, mode='r', encoding='utf8', newline='') as csvfile:
                r = csv.DictReader(csvfile, delimiter=';', fieldnames=['Player', 'Score'])
                _ = r.__next__()
                for row in r:
                    self._highscore.append((row['Player'], row['Score']))

    def write_scores(self):
        """
        overwrite the high score csv file with the current results
        :return:
        """
        if self._score_table_fp:
            with open(self._score_table_fp, mode='w', encoding='utf8', newline='') as csvfile:
                w = csv.DictWriter(csvfile, delimiter=';', fieldnames=['Player', 'Score'])
                w.writeheader()
                for (k, v) in self._highscore:
                    w.writerow({'Player': k, 'Score': v})

    def get_render_state(self) -> dict:
        return {
            'Player1': self._active_player.name,
            'Current_Tries': self.no_tries,
            'Max_Tries': self.max_tries,
            'Current_Guess': self.current_number,
            'Current_Score': self.score,
            'Player1_Won': self.player_has_won,
            'Finished': self.finished
        }


class GuessMyNumberRenderer(GameRenderer):
    """"""

    @property
    def game_active(self):
        return self._game_active

    def __init__(self, ):
        """Constructor for GuessTheNumberRenderer"""
        super(GuessMyNumberRenderer, self).__init__()
        self._game_active = False
        self.main_screen = MainScreen()
        self.options_screen = OptionsScreen()
        self.lboard_screen = LeaderBoardScreen()
        self.about_screen = AboutScreen()
        self.game_screen = GameScreen()

        self.game_screen.render = self.render_game

        self._wm.add_screen(self.main_screen, is_active=True)
        self._wm.add_screen(self.options_screen)
        self._wm.add_screen(self.lboard_screen)
        self._wm.add_screen(self.about_screen)
        self._wm.add_screen(self.game_screen)

        self._wm.add_transition(from_screen=self.main_screen, to_screen=self.options_screen)
        self._wm.add_transition(from_screen=self.main_screen, to_screen=self.lboard_screen)
        self._wm.add_transition(from_screen=self.main_screen, to_screen=self.about_screen)
        self._wm.add_transition(from_screen=self.main_screen, to_screen=self.game_screen)

        self._wm.add_transition(from_screen=self.game_screen, to_screen=self.main_screen)

        self._wm.on_transitioned = self._wm_on_transitioned
        self._font = pygame.font.Font(None, 36)
        self._textpos = None

    def _wm_on_transitioned(self, from_screen, to_screen):
        if to_screen == self.game_screen:
            self._game_active = True

    def render(self, buffer):
        self._wm.active_screen.render(buffer)
        # TODO: somehow we need to move the game state rendering into the game screen

    def render_game(self, buffer):
        buffer.fill((0, 0, 0, 255))

        if not self._game_state:
            raise ValueError("Game State not provided")

        state = self._game_state

        text_player = self._font.render("Player: {}".format(state['Player1']), 1, (0, 0, 255))
        text_tries  = self._font.render("Tries: {}/ {}".format(state['Current_Tries'], state['Max_Tries']), 1, (0, 255, 0))
        text_number = self._font.render("Your Guess: {}".format(state['Current_Guess']), 1, (0, 255, 0))
        text_score = self._font.render("Your Score: {}".format(state['Current_Score']), 1, (0, 255, 0))

        r_tries = text_tries.get_rect()
        r_number = text_number.get_rect()
        r_score = text_score.get_rect()

        buffer.blit(text_player, dest=(0, 0, 100, 100))
        buffer.blit(text_tries, dest=(buffer.get_width() - r_tries[2] - 10, 0, r_tries[2] + 10, r_tries[3]))
        buffer.blit(text_number, dest=(200, 200, 200, r_number[3]))

        if state['Finished']:
            text_finished = None
            if state['Player1_Won']:
                text_finished = self._font.render("You guessed right!", 1, (255, 255, 0))
                buffer.blit(text_score, dest=(200, 300, 200, r_score[3]))
            else:
                text_finished = self._font.render("Your time is up pal!", 1, (255, 255, 0))
            buffer.blit(text_finished, dest=(200, 250, 200, r_number[3]))


def is_number_key(k):
    return k in [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]


# TODO: LeaderBoardScreen
class LeaderBoardScreen(Screen):
    """"""

    def __init__(self, ):
        """Constructor for LeaderBoardScreen"""
        super(LeaderBoardScreen, self).__init__(name='screenLeaderBoard', title='LeaderBoard', width=640, height=480)

    def _initialize_components(self):
        self._about_label = Label(name='lblLeaderboard', x=10, y=10, w=300, caption="High Scores")
        self.add_component(self._about_label)

# TODO: OptionsScreen
class OptionsScreen(Screen):
    """"""

    def __init__(self, ):
        """Constructor for OptionsScreen"""
        super(OptionsScreen, self).__init__(name='screenOptions', title='Options', width=640, height=480)

    def _initialize_components(self):
        self._about_label = Label(name='lblOptions', x=10, y=10, w=300, caption="Options")
        self.add_component(self._about_label)

# TODO: AboutScreen
class AboutScreen(Screen):
    """"""

    def __init__(self, ):
        """Constructor for AboutScreen"""
        super(AboutScreen, self).__init__(name='screenAbout', title='About', width=640, height=480)

    def _initialize_components(self):
        self._about_label = Label(name='lblAbout', x=10, y=10, w=300, caption="About")
        self.add_component(self._about_label)


class MainScreen(Screen):
    """"""

    def __init__(self):
        """Constructor for MainScreen"""
        super().__init__(name='screenMain', title='Main', width=640, height=480)
        text = "Guess My Number"
        self._font = pygame.font.Font(pygame.font.get_default_font(), 32)
        self._header = self._font.render(text, 1, (64, 0, 255))

    def _main_on_click(self, sender, event_args):
        if sender.name == self.mni_quit.name:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif sender.name == self.mni_newgame.name:
            pygame.event.post(UIEvent.transition_screen(self.name, 'screenGame'))
        elif sender.name == self.mni_options.name:
            pygame.event.post(UIEvent.transition_screen(self.name, 'screenOptions'))
        elif sender.name == self.mni_leader.name:
            pygame.event.post(UIEvent.transition_screen(self.name, 'screenLeaderBoard'))
        elif sender.name == self.mni_about.name:
            pygame.event.post(UIEvent.transition_screen(self.name, 'screenAbout'))
        else:
            pass

    def _initialize_components(self):
        fs, fc, fstyle = 28, (192, 32, 128, 255), FontStyle.Normal
        self.main_menu = Menu('menuMain', caption='Main', show_caption=False, show_border=True, x=50, y=100)
        self.mni_newgame = MenuItem(name='mniNewGame', caption='New Game', font_size=fs, font_colour=fc, font_style=fstyle)
        self.mni_options = MenuItem(name='mniOptions', caption='Options', font_size=fs, font_colour=fc, font_style=fstyle)
        self.mni_leader  = MenuItem(name='mniLeaderBoard', caption='Leaderboard', font_size=fs, font_colour=fc, font_style=fstyle)
        self.mni_about   = MenuItem(name='mniAbout', caption='About', font_size=fs, font_colour=fc, font_style=fstyle)
        self.mni_quit = MenuItem(name='mniQuit', caption='Quit',
                                 font_size=fs, font_colour=fc, font_style=fstyle)

        # wire events
        self.mni_newgame.on_click = self._main_on_click
        self.mni_options.on_click = self._main_on_click
        self.mni_leader.on_click = self._main_on_click
        self.mni_about.on_click = self._main_on_click
        self.mni_quit.on_click = self._main_on_click

        self.main_menu.add_item(self.mni_newgame)
        self.main_menu.add_item(self.mni_options)
        self.main_menu.add_item(self.mni_leader)
        self.main_menu.add_item(self.mni_about)
        self.main_menu.add_item(self.mni_quit)

        self.add_component(self.main_menu)

    def render(self, buffer):
        Screen.render(self, buffer)
        buffer.blit(self._header, (50, 50))


class GameScreen(Screen):
    """"""
    def __init__(self):
        """Constructor for OptionsScreen"""
        super(GameScreen, self).__init__(name='screenGame', title='Guess My Number', width=640, height=480)


def main():
    if not pygame.font: raise("Pygame - fonts not loaded")
    if not pygame.mixer: raise("Pygame - audio not loaded")

    pygame.init()

    S_WIDTH = 640
    S_HEIGHT = 480
    S_TITLE = "Guess My Number"
    KEY_TO_DIGIT = {K_0: 0, K_1: 1, K_2: 2, K_3: 3, K_4: 4, K_5: 5, K_6: 6, K_7: 7, K_8: 8, K_9: 9}

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size(), flags=pygame.SRCALPHA)
    back_buffer = back_buffer.convert()
    back_buffer.fill((255, 255, 255, 255))

    # TODO: player needs to provide input in options
    p1 = Player(name='Player1', p_type=PlayerType.Human)
    the_game = GuessMyNumber()
    the_renderer = GuessMyNumberRenderer()
    wm = the_renderer.window_manager

    the_game.add_player(p1)

    the_game.init()

    is_done = False
    play_game = False
    clicker = 0
    while not is_done:

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicker = 1
                x, y = event.pos[0], event.pos[1]
                clicked, sender = wm.active_screen.clicked(mx=x, my=y, button=event.button)
                if clicked:
                    event_args = {
                        "x": x, "y": y, "button": event.button
                    }
                    sender.on_click(sender=sender, event_args=event_args)
            elif event.type == pygame.MOUSEBUTTONUP and clicker:
                wm.active_screen.unclick()
            elif event.type == pygame.USEREVENT:
                if event.mode == UIEvent.SCREEN_TRANSITION:
                    wm.transition(event.source, event.target)
                    clicker = 0  # reset the clicks so they are not processed by a transitioned element
            elif event.type == KEYDOWN and the_renderer.game_active:
                if event.key == K_RETURN:
                    the_game.commit_number()
                elif is_number_key(event.key):
                    the_game.add_digit(KEY_TO_DIGIT.get(event.key))
                else:
                    pass

        if the_renderer.game_active:
            the_game.update()
            gs = the_game.get_render_state()
            the_renderer.set_game_state(state=gs)

        # TODO: this should be done in the game renderer - as we have all the active windows there

        back_buffer.fill((255, 255, 255, 128))
        the_renderer.render(back_buffer)
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()

        # instead of breaking like before, we return to the main menu saving the score
        if the_game.finished:
            the_game.write_scores()
            pygame.time.delay(2000)
            pygame.event.post(UIEvent.transition_screen(wm.active_screen.name, 'screenMain'))

if __name__ == '__main__': main()
