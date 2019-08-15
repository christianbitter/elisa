# auth: christian bitter
# vers: 0.8
# This is a simple game, where the player has to guess a randomly generated integer number. This number has to be
# in some range [0, MAX]. The player is given some x amount of tries to guess the number
# The game will issue some informative, conversational messages to keep the player engaged.
# Messages are loaded from a csv file. These messages are provided for different guess directions (above, below) and
# magnitudes of overshooting or undershooting.
# TODO: add localization to german (VERSION 2)
# TODO: add messages for success and failure ends (VERSION 1.5).
# TODO: add a visual effect for success and failure ends (VERSION 1.5).
# While the player is guessing, we show a down-counting timer. If the timer counts down to zero, the player loses an
# attempt to take a guess. Once the player makes a guess, the timer is reset to its initial value.
# In a more difficult setting, the player has only some limited amount of seconds, before the clock ticks off.
# Other settings like maximum number of guessing attempts, and the shown guess history also depend on game difficulty.
# In easy and normal difficulty the history items are shown with hints (colour, text), such that the player has
# an indication as to whether she was above or below the target number.

# TODO: the screen interface needs to be improved. (VERSION 1.5)
#   TODO: a real background image needs to be drawn.
# The same image is shown on all screens.
# Leaderboard, options, and about screen have a back button.
# When clicking the back button, the player is navigated back to the main screen.
# Clicking on a button on the main screen's menu issues a click sound.
# TODO: except for the main playing screen, all screens feature a simple calm background music (VERSION 2)
# TODO: winning triggers a sound (VERSION 2)
# TODO: loosing triggers a sound (VERSION 2)
# TODO: timer running out triggers a sound (VERSION 2)
# A simple game menu, including ...
#  (start) new game
#  options
#   player name
#       Is captured via a simple text box component.
#       This allows players to input information when the control is in focus.
#   set difficulty
#       TODO: OptionsScreen - support changing difficulty. (VERSION 1.5)
#  view high score
#   Highscores are shown as formated single labels (rank, name, score).

#  view about ... this shows a simple whazz up/ credits text with a multi line label.
    #   The multiline label is composed of multiple rendered text lines'.
    #   A virtual line is created whenever the number of characters fitting on defined virtual screen line exceeds
    #   the available width. Words are broken on simple fragment delimiters like sentence punctuations.
#   Quit
#       Quits the game.
# menu items is shown.
# The main screen shows the menu, in the background we see numbers moving.
# the numbers fade in and out of visibility in the background.
# TODO: all screen declarations go into the game renderer.
# A game renderer has at least one active screen - the one where the game is rendered.
# A simple high score mechanism including persistence is realized. Initially, the score directly mimics the number of
# tries used to finish a round. Only if the player succeeds will she be awarded a score. There is no limitation in terms
# of best N to define the leaderboard - all entries are persisted and loaded.
# A particle that moves out of bounds cools down to a temperature of 0 and essentially is re-spawned.
# The particle renderer renders the circle (text) and a number inside to represent the thought bubbles of guessing a number.
# Game-specific settings are loaded from a json-configuration file.
# TODO: package things up
# TODO: clean things up
# TODO: write blog posts
# TODO: write book

import os
import csv
import json
import random
import pygame
from pygame.locals import *
from particle import ParticleSystem, Particle, _to_unit_vector, _angle_to_dir, ParticleSystemRenderer
from ui import Screen, UIEvent, Menu, MenuItem, FontStyle, Label, UIImage, MultiLineLabel, C_FORMBLUE, Button,\
    TextBox, FillStyle
from elisa import uifx
from elisa.game import Player, PlayerType, Game, GameDifficulty, GameRenderer
from collections import deque

ASSET_BASE_DIR_FP = "guess_my_number/asset"
GUESS_MY_NUMBER_BG_FP = "{}/gfx/background/guess_my_number_-_main_background_640_480.png".format(ASSET_BASE_DIR_FP)
BTN_BACK_UNCLICKED_FP = "{}/gfx/ui/button_back.png".format(ASSET_BASE_DIR_FP)
GUESS_MY_NUMBER_CREDITS_FP = "{}/data/credits.txt".format(ASSET_BASE_DIR_FP)
click_fp = "{}/sfx/click_01.ogg".format(ASSET_BASE_DIR_FP)

if not click_fp or not os.path.exists(click_fp):
    raise ValueError("You are missing {}".format(click_fp))


class GuessMyNumber(Game):
    """
    The guess my number game
    """
    VERSION = "0.8"

    STATE_NOT_STARTED = 0
    STATE_STARTED     = 1
    STATE_TIME_IS_UP  = -1
    STATE_PLAYER_WON  = -2
    STATE_PLAYER_GUESSED = -3
    STATE_PLAYER_IDLE = -4

    def __initialize_from_difficulty(self) -> bool:
        d = self._difficulty.name

        # check presence of keys
        check_keys = ['MaxNumberRange', 'MaxGuessAttempts', 'MaxCountDownValue', 'MaxGameHistoryLength']

        for ck in check_keys:
            if ck not in self._settings:
                return False

        self._max_number = self._settings['MaxNumberRange'][d]
        self._max_tries  = self._settings['MaxGuessAttempts'][d]
        self._downcounter_initial_value = self._settings['MaxCountDownValue'][d]
        self._guess_history_items = self._settings['MaxGameHistoryLength'][d]

        return True

    def __init__(self,
                 difficulty: GameDifficulty = GameDifficulty.MEDIUM,
                 debug: bool = False):
        """Constructor for GuessTheNumber"""
        super(GuessMyNumber, self).__init__(name='GuessTheNumber', max_players=1,
                                            description='A simple guess the number game')
        self._debug = debug
        self._difficulty = difficulty
        self._random_number = None
        self._no_tries = 0
        self._digit_buffer = []
        self._is_finished = False
        self._player_has_won = False
        self._guess = None
        self._highscore = []
        self._state = None
        self._score = None
        self._information = None
        self._active_player = None
        self._max_number = 0
        self._max_tries  = 0
        self._downcounter_initial_value = 0
        self._guess_history_items = 0
        self._downcounter = 0
        self._guess_history = []
        self._clock = pygame.time.Clock()
        self._ds = 0
        self._asset_base_fp = "guess_my_number/asset"
        self._score_table_fp= "guess_my_number_scores.csv"
        self._settings_fp   = os.path.join(self._asset_base_fp, "data/settings.json")
        self._message_table_fp = os.path.join(self._asset_base_fp, "data/message.csv")
        self._messages = []
        self._settings = {}
        self.__load_settings()

    def __load_settings(self):
        if not self._settings_fp or not os.path.exists(self._settings_fp):
            raise ValueError("Cannot load settings - file ('{}') does not exist".format(self._settings_fp))

        with open(self._settings_fp, 'r+', encoding='utf8') as fp_settings:
            self._settings = json.load(fp_settings)

    def init(self):
        if not self.__initialize_from_difficulty():
            raise ValueError("Could not obtain game settings ... defaulting not possible for now")

        self._score  = 0
        self._active_player = [v for _, v in self._players.items()][0]
        self.load_scores()
        self._load_messages()
        self._player_has_won = False
        self._is_finished = False
        self._no_tries = 0
        self._information = None
        self._digit_buffer = []
        self._downcounter = self._downcounter_initial_value
        self._guess_history = deque([], maxlen=self._guess_history_items)
        self._ds = 0
        self._state = GuessMyNumber.STATE_NOT_STARTED
        self._random_number = random.randint(0, self._max_number)

    def closeness_from_number(self, n:int):
        """
        determine how far our guess is from the number ... in qualitative terms.
        :param n:
        :return:
        """
        # VERY CLOSE, CLOSE, MEDIUM, FAR, VERY FAR
        if self._random_number == 0:
            diffp = 100
        else:
            diffp = round(100 * (abs(self._random_number - n) / self._random_number))
        closeness, undershot = None, (self._random_number - n) > 0
        if diffp < 10:  # very close
            closeness = "VERY CLOSE"
        elif diffp < 40:
            closeness = "CLOSE"
        elif diffp < 70:
            closeness = "MEDIUM"
        elif diffp < 100:
            closeness = "FAR"
        else:
            closeness = "VERY FAR"
        return closeness, undershot

    def start(self, **kwargs) -> None:
        self._state = GuessMyNumber.STATE_STARTED
        if self._debug:
            print("You have to guess: ", self._random_number)

    def end(self, **kwargs) -> None:
        g_state = kwargs.get('state', GuessMyNumber.STATE_PLAYER_IDLE)
        self._is_finished = True
        self._guess       = None
        self._downcounter = 0
        self._score = 0

        if g_state == GuessMyNumber.STATE_PLAYER_WON:
            self._player_has_won = True
            self._score = self._max_tries - self._no_tries
            self._highscore.append((self._active_player.name, self._score))
            self._information = 'Excellent Job! You are a little Sherlock Holmes.'
        elif g_state == GuessMyNumber.STATE_TIME_IS_UP:
            self._player_has_won = False
            self._information = 'Did you event try? Come on! One more round.'
        else:
            raise ValueError("unknown game state reached at end")

    def has_ended(self) -> tuple:
        """
        Check whether the game has ended already - either the player won, or the number of max attempts are reached.
        :return: (tuple) boolxint representing whether the game has ended and the code of the final game state
        """
        if self._no_tries >= self._max_tries:
            return True, GuessMyNumber.STATE_TIME_IS_UP

        n = self._guess
        if n is not None and isinstance(n, int):
            if n == self._random_number:
                return True, GuessMyNumber.STATE_PLAYER_WON
            else:
                return False, GuessMyNumber.STATE_PLAYER_GUESSED

        return False, GuessMyNumber.STATE_PLAYER_IDLE

    def update(self):
        if self._state == GuessMyNumber.STATE_NOT_STARTED:
            return

        self._ds = self._ds + self._clock.tick()
        if self._ds > 1000:
            self._downcounter -= 1
            self._ds -= 1000

        if self._downcounter == 0:
            self._no_tries += 1
            self._downcounter = self._downcounter_initial_value
            self._information = 'Unfortunately, your time is up ... Next try'

        g_has_ended, g_state = self.has_ended()

        if g_has_ended:
            self.end(state=g_state)
        else:
            # how far off are we ...
            if g_state == GuessMyNumber.STATE_PLAYER_GUESSED:
                closeness, undershot = self.closeness_from_number(self._guess)
                self._information = self.get_message(undershot, closeness)

                if self._debug:
                    print("You guessed: {} ... {}".format(self._guess, self._information))

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

    def get_message(self, direction: bool, limit: str):
        if direction:
            d_str = 'BELOW'  # undershot
        else:
            d_str = 'ABOVE'
        applicable_messages = [m for m in self._messages if m['category'] == d_str and m['degree'] == limit]
        random_message = 0
        return 'Unfortunately, your guess was {} {}'.format(limit, d_str), applicable_messages[random_message]

    @property
    def max_tries(self):
        return self._max_tries

    def commit_number(self):
        """
        When the player has hit the commit (enter) button, a new number is comitted to the game.
        :return: None
        """
        if len(self.current_number):
            self._no_tries += 1
            self._guess = int(self.current_number)
            self._digit_buffer = []
            self._downcounter = self._downcounter_initial_value
            closeness, undershot = self.closeness_from_number(self._guess)
            self._guess_history.append((self._guess, closeness, undershot))

    def add_digit(self, d) -> None:
        """
        add digit d to the digit buffer
        :param d: the digit to add
        :return: None
        """
        self._digit_buffer.append(d)

    def remove_digit(self) -> None:
        """
        remove/ erase the last digit from the current digit buffer
        :return None:
        """
        if len(self._digit_buffer) > 0:
            self._digit_buffer.pop(len(self._digit_buffer) - 1)

    def _load_messages(self):
        if not self._message_table_fp or not os.path.exists(self._message_table_fp):
            raise ValueError("_message_table_fp missing")

        with open(self._message_table_fp, mode='r', encoding='utf8', newline='') as csvfile:
            r = csv.DictReader(csvfile, delimiter=';', fieldnames=['category', 'degree', 'message'])
            _ = r.__next__()
            for row in r:
                x = {
                    'category': row['category'],
                    'degree': row['degree'],
                    'message': row['message']
                }
                self._messages.append(x)

    def load_scores(self) -> None:
        """
        Load the high score table from the respective csv. This updates the highscore field.
        highscore is a map from player name to
        :return:
        """
        if self._score_table_fp and os.path.exists(self._score_table_fp):
            with open(self._score_table_fp, mode='r', encoding='utf8', newline='') as csvfile:
                r = csv.DictReader(csvfile, delimiter=';', fieldnames=['Player', 'Score'])
                _ = r.__next__()
                for row in r:
                    self._highscore.append((row['Player'], row['Score']))

    def write_scores(self) -> None:
        """
        overwrite the high score csv file with the current results
        :return: (None)
        """
        if self._score_table_fp:
            self._highscore = sorted(self._highscore, key=lambda x: int(x[1]), reverse=True)

            with open(self._score_table_fp, mode='w', encoding='utf8', newline='') as csvfile:
                w = csv.DictWriter(csvfile, delimiter=';', fieldnames=['Player', 'Score'])
                w.writeheader()
                for (k, v) in self._highscore:
                    w.writerow({'Player': k, 'Score': v})

    @property
    def highscore(self):
        return self._highscore

    def get_render_state(self) -> dict:
        return {
            'Player1': self._active_player.name,
            'Current_Tries': self.no_tries,
            'Max_Tries': self.max_tries,
            'Highscores': self._highscore,
            'Attempts' : self._guess_history,
            'CountDownTimer': self._downcounter,
            'Current_Guess': self.current_number,
            'Current_Score': self.score,
            'Player1_Won': self.player_has_won,
            'Player1_Has_guessed': self._guess is not None,
            'Player1_Message': self._information,
            'Difficulty': self._difficulty,
            'State': self._state,
            'Settings': self._settings,
            'Finished': self.finished
        }

    @property
    def player_name(self):
        return self._active_player.name

    @property
    def difficulty(self):
        return self._difficulty

    @player_name.setter
    def player_name(self, v: str):
        if v is not None and len(v.strip()) > 0:
            self._active_player.name = v

    @difficulty.setter
    def difficulty(self, v):
        self._difficulty = v


class GuessMyNumberRenderer(GameRenderer):
    """"""

    @property
    def game_active(self):
        return self._game_active

    @game_active.setter
    def game_active(self, a: bool):
        self._game_active = a

    def __init__(self, ):
        """Constructor for GuessTheNumberRenderer"""
        GameRenderer.__init__(self)
        self._game_active = False
        self.main_screen = MainScreen()
        self.options_screen = OptionsScreen()
        self.lboard_screen = LeaderBoardScreen()
        self.about_screen = AboutScreen()
        self.game_screen = GameScreen()

        self.tdc = uifx.TwoDigitCounter(x=300, y=100, name='tdc', initial_value=60, colour=(64, 224, 64, 255))

        self._game_state = {}
        self.game_screen.render = self.__render_game

        self._wm.add_screen(self.main_screen, is_active=True)
        self._wm.add_screen(self.options_screen)
        self._wm.add_screen(self.lboard_screen)
        self._wm.add_screen(self.about_screen)
        self._wm.add_screen(self.game_screen)

        self._wm.add_transition(from_screen=self.main_screen, to_screen=self.options_screen, add_reverse=True)
        self._wm.add_transition(from_screen=self.main_screen, to_screen=self.lboard_screen, add_reverse=True)
        self._wm.add_transition(from_screen=self.main_screen, to_screen=self.about_screen, add_reverse=True)
        self._wm.add_transition(from_screen=self.main_screen, to_screen=self.game_screen)

        self._wm.add_transition(from_screen=self.game_screen, to_screen=self.main_screen)

        self._wm.on_transitioned = self._wm_on_transitioned
        self._font = pygame.font.Font(None, 36)
        self._textpos = None

    def _wm_on_transitioned(self, from_screen, to_screen) -> None:
        if to_screen == self.game_screen:
            self._game_active = True
            return

        self._game_active = False
        if to_screen == self.lboard_screen and 'Highscores' in self._game_state:
            self.lboard_screen.highscore = self._game_state['Highscores']

    def render(self, buffer):
        # fill the buffer with the background colour
        buffer.fill(self._wm.active_screen.background_colour)
        self._wm.active_screen.render(buffer)

    def __render_history(self, buffer):
        x_m, y_m, margin = 170, 280, 10
        difficulty = self._game_state['Difficulty']
        settings = self._game_state['Settings']
        hl = settings['MaxGameHistoryLength'][difficulty.name]
        h = self._font.render("X", 1, (0, 0, 0)).get_height() * hl

        pygame.draw.rect(buffer, (192, 192, 164), (x_m, y_m, 300, h + 2 * margin), 2)
        x_m, y_m = x_m + margin, y_m + margin
        hist = self._game_state['Attempts']
        x_i, y_i = x_m, y_m

        for i_hist in hist:
            undershot = i_hist[2]
            if undershot:
                str_exceeded = "guessed below"
                clr = (0, 0, 255)
            else:
                str_exceeded = "guessed above"
                clr = (255, 0, 0)

            text_item = self._font.render("{} - {}".format(str(i_hist[0]), str_exceeded), 1, clr)
            buffer.blit(text_item, dest=(x_i, y_i))
            y_i = y_i + text_item.get_height()

    def __render_game(self, buffer):
        buffer.fill((0, 0, 0, 255))

        if not self._game_state:
            raise ValueError("Game State not provided")

        state = self._game_state
        difficulty = self._game_state['Difficulty']
        settings = self._game_state['Settings']
        r = settings['MaxNumberRange'][difficulty.name]

        # TODO: these can be outsourced
        text_player = self._font.render("{} ({})".format(state['Player1'], state['Difficulty']), 1, (0, 0, 255))
        text_tries  = self._font.render("Tries: {}/ {}".format(state['Current_Tries'], state['Max_Tries']), 1, (0, 255, 0))
        text_command = self._font.render("You have to guess a number between {} and {}.".format(0, r), 1, (192, 192, 164))

        text_number = self._font.render("Your Guess: {}".format(state['Current_Guess']), 1, (0, 255, 0))
        text_score = self._font.render("Your Score: {}".format(state['Current_Score']), 1, (0, 255, 0))

        r_tries = text_tries.get_rect()
        r_number = text_number.get_rect()
        r_score = text_score.get_rect()
        r_player = text_player.get_rect()

        self.tdc.value = state["CountDownTimer"]
        self.tdc.update()

        buffer.blit(text_player, dest=(0, 0))
        buffer.blit(text_tries, dest=(buffer.get_width() - r_tries[2] - 10, 0, r_tries[2] + 10, r_tries[3]))
        buffer.blit(text_command, dest=(70, 150))
        buffer.blit(text_number, dest=(170, 220, 200, r_number[3]))
        buffer.blit(self.tdc.image, dest=(320 - (self.tdc.surface_width / 2), 10))

        if state['Finished']:
            if state['Player1_Won']:
                text_finished = self._font.render("You guessed right!", 1, (255, 255, 0))
                buffer.blit(text_score, dest=(170, 270, 200, r_score[3]))
            else:
                text_finished = self._font.render("Your time is up pal!", 1, (255, 255, 0))
            buffer.blit(text_finished, dest=(170, 270 + text_score.get_height(), 200, r_number[3]))

        else:
            self.__render_history(buffer)

            if state['Player1_Has_guessed']:
                g_msg, s_msg = state['Player1_Message']
                text_guess = self._font.render(s_msg['message'], 1, (255, 255, 0))
                buffer.blit(text_guess, dest=(170, 250, 200, r_score[3]))

            pass


def is_number_key(k):
    return k in [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]


class LeaderBoardScreen(Screen):
    """
    The leader board screen, i.e. where to show high scores and so on
    """

    m_max_entries = 10
    m_entry_margin = 3

    def _back_on_click(self, sender, event_args):
        pygame.event.post(UIEvent.transition_screen(self.name, 'screenMain'))

    def __init__(self):
        """Constructor for LeaderBoardScreen"""
        self._bg_img_fp = GUESS_MY_NUMBER_BG_FP
        self._btnBackUnclicked_fp = BTN_BACK_UNCLICKED_FP
        self._highscores = None
        super(LeaderBoardScreen, self).__init__(name='screenLeaderBoard', title='LeaderBoard', width=640, height=480)

    def _initialize_components(self):
        self._about_label = Label(name='lblLeaderboard', x=5, y=5, w=300, caption="High Scores")

        self._lbl_player_rank = Label('lblPlayerRank', x=40, y=70, w=60, caption='Rank')
        self._lbl_player_name = Label('lblPlayerName', x=103, y=70, w=200, caption='Player')
        self._lbl_player_score = Label('lblPlayerScore', x=306, y=70, w=200, caption='Score')

        y_i = 110
        lbl_margin = 3
        lbl_height = 30
        for i in range(10):
            lbl_player_rank_i = Label("lblPlayerRank_{}".format(i), x=40, y=y_i, w=60, h=lbl_height, caption='')
            lbl_player_name_i = Label("lblPlayerName_{}".format(i), x=103, y=y_i, w=200, h=lbl_height, caption='')
            lbl_player_score_i = Label("lblPlayerScore_{}".format(i), x=306, y=y_i, w=200, h=lbl_height, caption='')
            self.add_component(lbl_player_rank_i)
            self.add_component(lbl_player_name_i)
            self.add_component(lbl_player_score_i)
            y_i += lbl_height + lbl_margin

        image_margin = 10
        self.bg_image = UIImage(name='mnBGImage', image_fp=self._bg_img_fp,
                                x=image_margin, y=image_margin,
                                w=self.width - 2 * image_margin,
                                h=self.height - 2 * image_margin,
                                z=-2)
        self.btn_back = Button(name='btnBack', image_fp=self._btnBackUnclicked_fp, x=600, y=image_margin, w=32, h=32,
                               show_border=False, show_caption=False, fill_style=FillStyle.Image)
        self.btn_back.on_click = self._back_on_click
        self.add_component(self._about_label)
        self.add_component(self._lbl_player_rank)
        self.add_component(self._lbl_player_name)
        self.add_component(self._lbl_player_score)
        self.add_component(self.bg_image)
        self.add_component(self.btn_back)

    @property
    def highscores(self):
        return self._highscores

    @highscores.setter
    def highscore(self, v: dict):
        if v is not None:
            self._highscores = v
            self.__update_highscore_table()
            Screen.invalidate(self)

    def __update_highscore_table(self):
        for i, h in enumerate(self._highscores):
            if i == LeaderBoardScreen.m_max_entries:
                break
            lbl_rank_i = self["lblPlayerRank_{}".format(i)]
            lbl_player_name_i = self["lblPlayerName_{}".format(i)]
            lbl_player_score_i = self["lblPlayerScore_{}".format(i)]
            lbl_rank_i.caption = str(i)
            lbl_player_name_i.caption = str(self._highscores[i][0])
            lbl_player_score_i.caption = str(self._highscores[i][1])


class OptionsScreen(Screen):
    """
    setting of game configuration and player details
    """

    def _back_on_click(self, sender, event_args):
        pygame.event.post(UIEvent.transition_screen(self.name, 'screenMain'))

    def _btn_ok_click(self, sender, event_args):
        # transition back to main screen, where we will store the modified name
        pygame.event.post(UIEvent.transition_screen(self.name, 'screenMain'))

    def __init__(self, ):
        """Constructor for OptionsScreen"""
        self._bg_img_fp = GUESS_MY_NUMBER_BG_FP
        self._btnBackUnclicked_fp = BTN_BACK_UNCLICKED_FP
        super(OptionsScreen, self).__init__(name='screenOptions', title='Options', width=640, height=480)

    @property
    def player_name(self):
        return self.txt_player_name.caption

    def difficulty(self):
        return self.lbl_difficultys.caption

    def _initialize_components(self):
        self.lbl_about = Label(name='lblOptions', x=5, y=5, w=300, caption="Options")
        self.lbl_player_name = Label(name='lblPlayerName', x=50, y=200, w=130, caption="Player Name")
        self.txt_player_name = TextBox(name='txtPlayerName', x=200, y=200, w=150, caption='Player1')

        self.lbl_difficulty  = Label(name='lblDifficulty', x=50, y=240, w=130, caption="Difficulty")
        self.lbl_difficultys = Label(name='lblDifficultys', x=200, y=240, w=150, caption="Medium", show_border=False)
        self.btn_ok          = Button(name='btnOK', x=300, y=350, caption='OK')

        image_margin = 10
        self.bg_image = UIImage(name='mnBGImage', image_fp=self._bg_img_fp,
                                x=image_margin, y=image_margin,
                                w=self.width - 2 * image_margin,
                                h=self.height - 2 * image_margin,
                                z=-2)
        self.btn_back = Button(name='btnBack', image_fp=self._btnBackUnclicked_fp, x=600, y=image_margin, w=32, h=32,
                               show_border=False, show_caption=False, fill_style=FillStyle.Image)
        self.btn_back.on_click = self._back_on_click
        self.btn_ok.on_click = self._btn_ok_click

        self.add_component(self.lbl_about)
        self.add_component(self.lbl_player_name)
        self.add_component(self.txt_player_name)
        self.add_component(self.lbl_difficulty)
        self.add_component(self.lbl_difficultys)
        self.add_component(self.bg_image)
        self.add_component(self.btn_back)
        self.add_component(self.btn_ok)


class AboutScreen(Screen):
    """
    The about screen ... where to show credits etc.
    """

    def _back_on_click(self, sender, event_args):
        pygame.event.post(UIEvent.transition_screen(self.name, 'screenMain'))

    def __init__(self, ):
        """Constructor for AboutScreen"""
        self._bg_img_fp = GUESS_MY_NUMBER_BG_FP
        self._btnBackUnclicked_fp = BTN_BACK_UNCLICKED_FP
        self._credits_fp = GUESS_MY_NUMBER_CREDITS_FP
        self._credits_str= None
        self.__load_credits__()

        super(AboutScreen, self).__init__(name='screenAbout', title='About', width=640, height=480,
                                          background_colour=C_FORMBLUE)

    def __load_credits__(self):
        if self._credits_fp is None or not os.path.exists(self._credits_fp):
            raise ValueError("Credits file not defined")
        with open(self._credits_fp, 'r+', encoding='utf8') as f:
            self._credits_str = f.read()

    def _initialize_components(self):
        self._about_label = Label(name='lblAbout', x=5, y=5, w=300, caption="About")
        image_margin  = 10
        self.bg_image = UIImage(name='mnBGImage', image_fp=self._bg_img_fp,
                                x=image_margin, y=image_margin,
                                w=self.width - 2 * image_margin,
                                h=self.height - 2 * image_margin,
                                z=-2)
        self.btn_back = Button(name='btnBack', image_fp=self._btnBackUnclicked_fp, x=600, y=image_margin, w=32, h=32,
                               show_border=False, show_caption=False, fill_style=FillStyle.Image)
        self._lblTitle = Label(name='lblTitle', x=200, y=30, caption='Guess My Number',
                               show_border=False, fill_style=FillStyle.Empty, font_colour=(255, 255, 255))
        self._lblCredits = MultiLineLabel(name='lblCredits', x=100, y=100, width=400, caption=self._credits_str,
                                          show_border=True, fill_style=FillStyle.Colour)

        self.btn_back.on_click = self._back_on_click
        self.add_component(self.bg_image)
        self.add_component(self._about_label)
        self.add_component(self.btn_back)
        self.add_component(self._lblTitle)
        self.add_component(self._lblCredits)


class MainScreen(Screen):
    """
    The main entry screen
    """

    def __init__(self):
        """Constructor for MainScreen"""
        self._bg_img_fp = GUESS_MY_NUMBER_BG_FP
        Screen.__init__(self, name='screenMain', title='Main', width=640, height=480)
        self._click_sfx = pygame.mixer.Sound(click_fp)
        self._t_last = pygame.time.get_ticks()
        self._delta_t= 0  # in seconds
        self._number_psys = ParticleSystem(max_particles=40)
        self._psys_renderer = GMNParticleSystemRenderer()
        self._number_psys.on_particle_died = lambda psys, particle: self.particle_died(psys, particle)

        for _ in range(self._number_psys.max_particles):
            self._number_psys.add_particle(self._random_particle())

    def _random_particle(self):
        temp_decrease = 0.2 * random.random()
        particle_size = random.randint(1, 20)
        max_particle_velocity = random.randint(0, 60)
        G_DIR = _to_unit_vector(_angle_to_dir(90))
        G_FORCE = (0 * G_DIR[0], G_DIR[1] * 9.81)
        velocity = [max_particle_velocity, max_particle_velocity]
        alpha = int(random.random() * 360)
        dir = _to_unit_vector(_angle_to_dir(alpha))
        v = (dir[0] * velocity[0], dir[1] * velocity[1])
        p = GMNParticle(pos=(random.randint(0, self.width), random.randint(0, self.height)),
                        temperature=.7, temp_decrease=temp_decrease, size=particle_size,
                        velocity=v, max_velocity=max_particle_velocity,
                        acceleration=G_FORCE, max_acceleration=-1)
        return p

    def particle_died(self, psys, particle) -> None:
        """
        whenever a particle dies, we create a new particle
        :param psys: (ParticleSystem) the particle system we live in
        :param particle: (Particle) the dying particle
        :return: None
        """
        psys.add_particle(self._random_particle())

    def _main_on_click(self, sender, event_args):
        # play the click sound
        self._click_sfx.play(maxtime=200)
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
        self.main_menu = Menu('menuMain', caption='Main', show_caption=False, show_border=True, x=30, y=50)
        self.mni_newgame = MenuItem(name='mniNewGame', caption='New Game', font_size=fs, font_colour=fc, font_style=fstyle)
        self.mni_options = MenuItem(name='mniOptions', caption='Options', font_size=fs, font_colour=fc, font_style=fstyle)
        self.mni_leader  = MenuItem(name='mniLeaderBoard', caption='Leaderboard', font_size=fs, font_colour=fc, font_style=fstyle)
        self.mni_about   = MenuItem(name='mniAbout', caption='About', font_size=fs, font_colour=fc, font_style=fstyle)
        self.mni_quit = MenuItem(name='mniQuit', caption='Quit', font_size=fs, font_colour=fc, font_style=fstyle)

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

        image_margin  = 10
        self.bg_image = UIImage(name='mnBGImage', image_fp=self._bg_img_fp,
                                x=image_margin, y=image_margin,
                                w=self.width - 2 * image_margin,
                                h=self.height - 2 * image_margin,
                                z=-2)

        self.title_label = Label(name='lblTitle', x=5, y=5, w=300, caption="Guess My Number")
        self.version_label = Label(name='lblVersion', x=5, y=self.height - 30,
                                   caption="Version: {}".format(GuessMyNumber.VERSION))

        self.add_component(self.title_label)
        self.add_component(self.version_label)
        self.add_component(self.bg_image)
        self.add_component(self.main_menu)
        self.add_component(self.title_label)

    def render(self, buffer):
        tl = pygame.time.get_ticks()

        Screen.invalidate(self)
        Screen._paint(self)
        self._delta_t = 0.001 * (tl - self._t_last)
        self._t_last = tl
        self._number_psys.update(t=self._delta_t)
        # check each particle if it is out of bounds
        for p in self._number_psys.particles:
            if 0 <= p.x < self.width and 0 <= p.y < self.height:
                continue
            else:
                p.temperature = 0.0

        Screen.render(self, buffer)
        self._psys_renderer.render(buffer, self._number_psys.particles)
        # buffer.blit(self.bg_image.image, (0, 0))#, special_flags=pygame.BLEND_MAX)


class GameScreen(Screen):
    """"""
    def __init__(self):
        """Constructor for GameScreen"""
        super(GameScreen, self).__init__(name='screenGame', title='Guess My Number', width=640, height=480,
                                         background_colour=(32, 32, 32))
        self._tdc = None
        self._lbl_player = None
        self._lbl_tries  = None
        self._lbl_command= None
        self._lbl_number = None
        self._lbl_score  = None

    def _initialize_components(self):
        # TODO: get game state in and update the labels
        # self._font.render("{} ({})".format(state['Player1'], state['Difficulty']), 1, (0, 0, 255))
        self._lbl_player = Label(name='lblPlayerName', x=0, y=0, caption="TODO: Player Name",
                                 font_colour=(0, 0, 255), fill_style=FillStyle.Empty, show_border=False)
        # self._font.render("Tries: {}/ {}".format(state['Current_Tries'], state['Max_Tries']), 1, (0, 255, 0))
        self._lbl_tries  = Label(name='lblAttempts', x=self._w - 150, y=0, caption='Tries: TODO',
                                 font_colour=(0, 255, 0), fill_style=FillStyle.Empty, show_border=False)
        # self._font.render("You have to guess a number between {} and {}.".format(0, r), 1, (192, 192, 164))
        self._lbl_command= Label(name='lblCommand', x=70, y=150, caption="You have to guess a number between 0 and 10.",
                                 font_colour=(192, 192, 164), fill_style=FillStyle.Empty, show_border=False)
        # self._font.render("Your Guess: {}".format(state['Current_Guess']), 1, (0, 255, 0))
        self._lbl_number = Label(name='lblNumber', x=170, y=220, caption="Your Guess: TODO",
                                 font_colour=(0, 255, 0), fill_style=FillStyle.Empty, show_border=False)
        # self._font.render("Your Score: {}".format(state['Current_Score']), 1, (0, 255, 0))
        self._lbl_score = Label(name='lblScore', x=170, y=270, caption="Your Score: TODO",
                                font_colour=(0, 255, 0), fill_style=FillStyle.Empty, show_border=False, visible=False)

        self._tdc = uifx.TwoDigitCounter(x=250, y=10, name='tdc',
                                         initial_value=60, colour=(64, 224, 64, 255))

        self.add_component(self._lbl_player)
        self.add_component(self._lbl_tries)
        self.add_component(self._lbl_command)
        self.add_component(self._lbl_number)
        self.add_component(self._lbl_score)
        self.add_component(self._tdc)


class GMNParticle(Particle):
    """"""

    def __init__(self, pos, size: int,
                 temperature:float, temp_decrease,
                 velocity, max_velocity, acceleration, max_acceleration,
                 minno: int = 0, maxno: int = 10):
        """Constructor for GMNParticle"""
        self._number = random.randint(minno, maxno)
        super(GMNParticle, self).__init__(pos, size, temperature, temp_decrease,
                                          velocity, max_velocity,
                                          acceleration, max_acceleration)

    @property
    def number(self):
        return self._number


class GMNParticleSystemRenderer(ParticleSystemRenderer):
    """"""

    def __init__(self):
        """Constructor for GMNParticleSystemRenderer"""
        super(GMNParticleSystemRenderer, self).__init__()

    def temperature2colour(self, temperature:float) -> tuple:
        return int(temperature * 164), int(64 * temperature), int(temperature * 255), 255

    def render(self, buffer, render_items: list, x: int = None, y: int = None):
        if not render_items or len(render_items) < 1:
            return
        C_WHITE = (255, 255, 255, 255)
        w, h = buffer.get_width(), buffer.get_height()
        p = [0, 0]
        if x is not None:
            if not (0 <= x < w):
                raise ValueError("x outside of viewport")
            p[0] = x
        if y is not None:
            if not (0 <= y < h):
                raise ValueError("y outside of viewport")
            p[1] = y

        for particle in render_items:
            col = self.temperature2colour(particle.temperature)
            if len(col) != 4:
                raise ValueError("temperature2colour must yield an RGBA tuple")
            if 0 <= particle.x < w and 0 <= particle.y < h:
                font = pygame.font.Font(None, particle.size)
                text = font.render(str(particle.number), 1, C_WHITE)
                textpos = text.get_rect()
                textpos.centerx = particle.x
                textpos.centery = particle.y

                pygame.draw.circle(buffer, col, (int(particle.x), int(particle.y)), particle.size, 0)
                pygame.draw.circle(buffer, (128, 128, 128, int(255*particle.temperature)),
                                   (int(particle.x), int(particle.y)),
                                   particle.size, 1)
                buffer.blit(text, textpos)


def main():
    if not pygame.font:
        raise("Pygame - fonts not loaded")
    if not pygame.mixer:
        raise("Pygame - audio not loaded")

    pygame.init()

    w, h, t = 640, 480, "Guess My Number"
    KEY_TO_DIGIT = {K_0: 0, K_1: 1, K_2: 2, K_3: 3, K_4: 4, K_5: 5, K_6: 6, K_7: 7, K_8: 8, K_9: 9}

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size(), flags=pygame.SRCALPHA)
    back_buffer = back_buffer.convert()
    back_buffer.fill((255, 255, 255, 255))

    # TODO: player needs to provide input in options
    p1 = Player(name='Player1', p_type=PlayerType.Human)
    the_game = GuessMyNumber(debug=True, difficulty=GameDifficulty.MEDIUM)
    the_renderer = GuessMyNumberRenderer()
    wm = the_renderer.window_manager

    the_game.add_player(p1)
    the_game.init()

    # TODO: this can move into the game
    clock = pygame.time.Clock()
    is_done = False
    clicker = 0
    while not is_done:
        millis_passed = clock.tick()

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicker = 1
                x, y = event.pos[0], event.pos[1]
                clicked, sender = wm.active_screen.clicked(mx=x, my=y, button=event.button)
                if clicked:
                    event_args = { "x": x,
                                   "y": y,
                                   "button": event.button }
                    sender.on_click(sender=sender, event_args=event_args)
            elif event.type == pygame.MOUSEBUTTONUP and clicker:
                wm.active_screen.unclick()
            elif event.type == pygame.USEREVENT:
                # TODO: when we transition from the options screen back ... we update the relevant settings
                if event.mode == UIEvent.SCREEN_TRANSITION:
                    wm.transition(event.source, event.target)
                    clicker = 0
                    if event.target == wm.active_screen.name and wm.active_screen.name == 'screenGame':
                        the_game.start()
                    elif event.source == 'screenOptions':
                        player_name = wm[event.source].player_name
                        the_game.player_name = player_name

            elif event.type == KEYDOWN:
                if the_renderer.game_active:  # we are in the game screen
                    if event.key == K_RETURN:
                        the_game.commit_number()
                    elif is_number_key(event.key):
                        the_game.add_digit(KEY_TO_DIGIT.get(event.key))
                    elif event.key == K_BACKSPACE:
                        the_game.remove_digit()
                    else:
                        pass
                else:
                    wm.process_event(event)

        wm.update(t=millis_passed)

        if the_renderer.game_active:
            the_game.update()

        gs = the_game.get_render_state()
        the_renderer.set_game_state(state=gs)

        back_buffer.fill((0, 0, 0, 255))
        the_renderer.render(back_buffer)
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()

        if the_game.finished and the_renderer.game_active:
            the_renderer.game_active = False
            the_game.write_scores()
            pygame.time.delay(2000)
            pygame.event.post(UIEvent.transition_screen(wm.active_screen.name, 'screenMain'))
            the_game.init()


if __name__ == '__main__':
    main()

