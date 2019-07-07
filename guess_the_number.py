# auth: christian bitter
# vers: 0.1
# This is a simple game, where the player has to guess a randomly generated integer number. This number has to be
# in some range [0, MAX]. The player is given some x amount of tries to guess the number

# TODO: simple asset store
# TODO: the game will issue some informative, conversational messages to keep the player engaged
#   Messages are loaded from a csv file.
# TODO: while the player is guessing, we show the elisa running sprite
#   The running is virtual, i.e. we move some arbirary other sprite like a simple point or we can use the tree in the
#   tileset/tileset.png, past elisa.
#   TODO: This involves the creation of a parallax scrolling effect.
#       This means while the foreground (elisa) is animated to show moving,
#       the background moves at a much lower pace than induced by the foreground.
# TODO: in a more difficult setting, the player has only some amount of seconds, before the clock ticks off
#   This will be visualized by Elisa moving from the starting position to the end position. The end is marked by the
#   tree.
# TODO: the screen interface needs to be improved.
#   TODO: a real background image needs to be drawn.
#    TODO: The same image is shown on all screens.
#    TODO: leaderboard, options, and about screen need a back button.
#       TODO: when clicking the back button, the player is navigated back to the main screen.
# TODO: except for the main playing screen, all screens feature a simple calm background music
# TODO: clicking on a menu item will issue a click sound.
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
    #   The multiline label is composed of multiple virtual individual line 'labels'.
    #   A virtual line is created whenever the number of characters fitting on defined virtual screen line exceeds
    #   the available width. Breaking words should reflect the standard orthography.
#   Quit
#       Quits the game.
# menu items is shown.
# The main screen shows the menu, in the background we see numbers moving.
# the numbers fade in and out of visibility in the background.
# TODO: all screen declarations go into the game renderer
# A game renderer has at least one active screen - the one where the game is rendered.
# A simple high score mechanism including persistence is realized. Initially, the score directly mimics the number of
# tries used to finish a round. Only if the player succeeds will she be awarded a score. There is no limitation in terms
# of best N to define the leaderboard - all entries are persisted and loaded.
# A particle that moves out of bounds cools down to a temperature of 0 and essentially is respawned.
# The particle renderer renders the circle (text) and a number inside to represent the thought bubbles of guessing a number.

import os
import csv
import uuid
import random
import pygame
from pygame.locals import *
from enum import Enum
from particle import ParticleSystem, Particle, _to_unit_vector, _angle_to_dir, ParticleSystemRenderer
from ui import Screen, UIEvent, Menu, MenuItem, FontStyle, Label, UIImage, WindowManager, Canvas

ASSET_BASE_DIR_FP = "guess_my_number/asset"
GUESS_MY_NUMBER_BG_FP = "{}/gfx/background/guess_my_number_-_main_background_640_480.png".format(ASSET_BASE_DIR_FP)
BTN_BACK_UNCLICKED_FP = "{}/gfx/ui/button_back.png".format(ASSET_BASE_DIR_FP)

class PlayerType(Enum):
    """
    Enumeration of different player types.
    """
    CPU = 1
    Human = 2

    def __str__(self):
        return self.name


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

    def __eq__(self, other):
        return self._id == other.id

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def player_type(self):
        return self._type

    def __repr__(self):
        return "{} ({}: {})".format(self._name, self._type, self._id)


class Game(object):
    """
    Base class of our games
    """

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
        self._asset_base_fp = "guess_my_number/asset"

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
        self._bg_img_fp = GUESS_MY_NUMBER_BG_FP
        self._btnBackUnclicked_fp = BTN_BACK_UNCLICKED_FP
        super(LeaderBoardScreen, self).__init__(name='screenLeaderBoard', title='LeaderBoard', width=640, height=480)

    def _initialize_components(self):
        self._about_label = Label(name='lblLeaderboard', x=10, y=10, w=300, caption="High Scores")
        image_margin = 10
        self.bg_image = UIImage(name='mnBGImage', image_fp=self._bg_img_fp,
                                x=image_margin, y=image_margin,
                                w=self.width - 2 * image_margin,
                                h=self.height - 2 * image_margin,
                                z=-2)
        self._btnBack = UIImage(name='btnBack', image_fp=self._btnBackUnclicked_fp, x=600, y=image_margin, w=32, h=32)
        self.add_component(self._about_label)
        self.add_component(self.bg_image)
        self.add_component(self._btnBack)

# TODO: OptionsScreen
class OptionsScreen(Screen):
    """"""

    def __init__(self, ):
        """Constructor for OptionsScreen"""
        self._bg_img_fp = GUESS_MY_NUMBER_BG_FP
        self._btnBackUnclicked_fp = BTN_BACK_UNCLICKED_FP
        super(OptionsScreen, self).__init__(name='screenOptions', title='Options', width=640, height=480)

    def _initialize_components(self):
        self._about_label = Label(name='lblOptions', x=10, y=10, w=300, caption="Options")
        image_margin = 10
        self.bg_image = UIImage(name='mnBGImage', image_fp=self._bg_img_fp,
                                x=image_margin, y=image_margin,
                                w=self.width - 2 * image_margin,
                                h=self.height - 2 * image_margin,
                                z=-2)
        self._btnBack = UIImage(name='btnBack', image_fp=self._btnBackUnclicked_fp, x=600, y=image_margin, w=32, h=32)
        self.add_component(self._about_label)
        self.add_component(self.bg_image)
        self.add_component(self._btnBack)

# TODO: AboutScreen
class AboutScreen(Screen):
    """"""

    def __init__(self, ):
        """Constructor for AboutScreen"""
        self._bg_img_fp = GUESS_MY_NUMBER_BG_FP
        self._btnBackUnclicked_fp = BTN_BACK_UNCLICKED_FP
        super(AboutScreen, self).__init__(name='screenAbout', title='About', width=640, height=480)

    def _initialize_components(self):
        self._about_label = Label(name='lblAbout', x=10, y=10, w=300, caption="About")
        image_margin  = 10
        self.bg_image = UIImage(name='mnBGImage', image_fp=self._bg_img_fp,
                                x=image_margin, y=image_margin,
                                w=self.width - 2 * image_margin,
                                h=self.height - 2 * image_margin,
                                z=-2)
        self._btnBack = UIImage(name='btnBack', image_fp=self._btnBackUnclicked_fp, x=600, y=image_margin, w=32, h=32)
        self.add_component(self._about_label)
        self.add_component(self.bg_image)
        self.add_component(self._btnBack)


class MainScreen(Screen):
    """"""

    # TODO: the main screen shows some number tiles, i.e. rects with numbers on them
    #       spawning at random locations
    #       moving into random locations
    #       rotating around random angles
    #       living and disappearing

    def __init__(self):
        """Constructor for MainScreen"""
        text = "Guess My Number"
        self._bg_img_fp = GUESS_MY_NUMBER_BG_FP
        super().__init__(name='screenMain', title='Main', width=640, height=480)

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

    def particle_died(self, psys, particle):
        # create a new particle
        psys.add_particle(self._random_particle())

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

        # TODO: support transparent blitting of images
        # TODO: support the drawing of the particle system into a canvas element
        image_margin  = 10
        self.bg_image = UIImage(name='mnBGImage', image_fp=self._bg_img_fp,
                                x=image_margin, y=image_margin,
                                w=self.width - 2 * image_margin,
                                h=self.height - 2 * image_margin,
                                z=-2)

        self.title_label = Label(name='lblTitle', x=5, y=5, w=300, caption="Guess My Number")
        self.add_component(self.title_label)

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
        super(GameScreen, self).__init__(name='screenGame', title='Guess My Number', width=640, height=480)


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
