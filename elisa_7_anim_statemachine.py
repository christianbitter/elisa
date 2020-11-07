# auth: christian bitter
# desc: this is based on elisa4 and 5
#       we couple the state machine with animation and make movement slightly more realistic.
#       that is, moving right, will move the player right until an imaginary wall is hit

from pygame.locals import *
from sm import *
from sprites import SpriteMap
import os
import pygame


class Elisa(pygame.sprite.Sprite):
    def __init__(self, sm:StateMachine, pos):
        super(Elisa, self).__init__()
        self._state_machine = sm
        self._current_animation_frame = 0
        self._current_state = sm.current.name
        self._current_sprite = None
        self._assets = SpriteAssetManager()
        self._position = pos
        anims = ["WALK_RIGHT", "WALK_LEFT", "JUMP", "IDLE"]
        descfps = ['asset/elise_character/tileset_elisa_walk@8x.json',
                   'asset/elise_character/tileset_elisa_walk@8x.json',
                   'asset/elise_character/tileset_elisa_walk_jump@8x.json',
                   'asset/elise_character/tileset_elisa_idle@8x.json']
        for key, fp in zip(anims, descfps):
            self._assets.add_sprite_map(name=key, metadata_fp=fp)
        self._sprites = {
            'Idle': self._assets.get_sprite(sprite_map_name='IDLE'),
            'Walk_Right': self._assets.get_sprite(sprite_map_name='WALK_RIGHT'),
            'Walk_Left': self._assets.get_sprite(sprite_map_name='WALK_LEFT'),
            'Jump': self._assets.get_sprite(sprite_map_name='JUMP')
        }

    def _right(self):
        if self._position[0] < 500:
            self._position = (self._position[0] + 3, self._position[1])

    def _left(self):
        if self._position[0] > 100:
            self._position = (self._position[0] - 3, self._position[1])

    def update(self):
        self._state_machine.update()

        if self._state_machine.current.name != self._current_state:
            self._current_animation_frame = 0
            self._current_state = self._state_machine.current.name
        else:
            self._current_animation_frame += 1
            if self._current_animation_frame >= self._sprites[self._current_state].no_sprites:
                self._current_animation_frame = 0

        if self._current_state == 'Walk_Right':
            self._right()
        elif self._current_state == 'Walk_Left':
            self._left()
        else:
            pass

        self._current_sprite = self._sprites[self._current_state][self._current_animation_frame]

    @property
    def assets(self):
        return self._assets

    @property
    def current_state(self):
        return self._state_machine.current

    @property
    def current_sprite(self):
        return self._current_sprite

    @property
    def current_frame(self):
        return self._current_animation_frame

    @property
    def position(self):
        return self._position


class SpriteAssetManager(object):
    def __init__(self):
        """Constructor for AssetManager"""
        super(SpriteAssetManager, self).__init__()
        self._assets = {}

    def __repr__(self):
        return "Registered Assets ({}): {}".format(len(self._assets), self._assets.keys())

    def add_sprite_map(self, name:str, metadata_fp:str, initialize:bool = True):
        if not name: raise ValueError('name not provided')
        if not metadata_fp: raise ValueError('metadata file not provided')
        if name in self._assets: raise ValueError('asset already registered')
        if not os.path.exists(metadata_fp): raise ValueError('metadata file does not exist')

        self._assets[name] = SpriteMap(metadata_fp)
        if initialize:
            self._assets[name].initialize()

    def get_sprite(self, sprite_map_name:str, sprite:str = None):
        if not sprite_map_name:
            raise ValueError("Asset cannot be none")
        if sprite_map_name not in self._assets:
            raise ValueError("Unknown asset '{}'".format(sprite_map_name))
        sm = self._assets[sprite_map_name]
        if not sprite:
            return sm
        if sprite not in sm:
            raise ValueError("Undefined sprite '{}' selected".format(sprite))
        return sm[sprite]

    def initialize(self, name:str = None):
        if not name:
            for a in self._assets:
                if not a.initialized:
                    a.initialize()
        else:
            if name not in self._assets: raise ValueError('not an asset')
            if not self._assets[name].initialized:
                self._assets[name].initialize()

def main():
    if not pygame.font: print("Pygame - fonts not loaded")
    if not pygame.mixer: print("Pygame - audio not loaded")

    # init pygame - create the main window, and a background surface
    pygame.init()

    S_WIDTH = 800
    S_HEIGHT= 600
    S_TITLE = "Elisa - Statemachine and GFX"

    C_WHITE = (250, 250, 250)
    C_BLUE = (0, 0, 255)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    # FPS watcher
    fps_watcher = pygame.time.Clock()
    is_done = False

    # Display some text
    font = pygame.font.Font(None, 36)
    text = font.render("You pressed: <PLACEHOLDER>", 1, C_BLUE)
    textpos = text.get_rect()
    textpos.centerx = back_buffer.get_rect().centerx - 200
    textpos.centery = back_buffer.get_rect().centery + 100

    key_map = pygame.key.get_pressed()
    pressed = False

    idle = State("Idle", "The idle state")
    walk_r = State("Walk_Right", "The walking state")
    walk_l = State("Walk_Left", "The walking state")

    jump = State("Jump", "The jumping state")

    def idle_to_walk_right():
        return key_map[K_RIGHT]

    def idle_to_walk_left():
        return key_map[K_LEFT]

    def idle_to_jump():
        return key_map[K_UP]

    def jump_to_idle():
        return not key_map[K_UP]

    def walk_right_to_idle():
        return not key_map[K_RIGHT]

    def walk_left_to_idle():
        return not key_map[K_LEFT]

    t_idle_walk_left = Transition(idle, walk_l, idle_to_walk_left, "IDLE_WALK_LEFT", "From Idle to Walk Left")
    t_idle_walk_right= Transition(idle, walk_r, idle_to_walk_right, "IDLE_WALK_RIGHT", "From Idle to Walk Right")

    t_walk_left_idle = Transition(walk_l, idle, walk_left_to_idle, "WALK_LEFT_IDLE", "From Walk Left To Idle")
    t_walk_right_idle = Transition(walk_r, idle, walk_right_to_idle, "WALK_RIGHT_IDLE", "From Walk Right To Idle")

    t_idle_jump = Transition(idle, jump, idle_to_jump, "IDLE_JUMP", "From Idle to Jump")
    t_jump_idle = Transition(jump, idle, jump_to_idle, "JUMP_IDLE", "From Jump to Idle")

    sm = StateMachine(states=[idle, walk_l, walk_r, jump],
                      transitions=[t_idle_walk_left, t_idle_walk_right, t_idle_jump,
                                   t_walk_left_idle, t_walk_right_idle, t_jump_idle],
                      initial_state=idle)

    elisa = Elisa(sm=sm, pos=(100, 100))

    while not is_done:
        fps_watcher.tick(25)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

            key_map = pygame.key.get_pressed()

        elisa.update()
        text = font.render("Current State: {} ({})".format(elisa.current_state.name, elisa.position), 1, C_BLUE)
        back_buffer.fill(C_WHITE)
        back_buffer.blit(text, textpos)
        back_buffer.blit(elisa.current_sprite.image, elisa.position)

        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()
