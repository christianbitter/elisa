# auth: christian bitter
# desc: this is based on elisa 7
#       It introduces a second elisa sprite offset to the right.
#       This elisa also has a state machine attached.
#       The second state machine listens on the a, d and w keys for left, right and jump.
#       When elisas collides with each other further movement is restricted, i.e. they cannot pass each other

from pygame.locals import QUIT, K_LEFT, K_RIGHT, K_DOWN, K_UP, K_a, K_s, K_w, K_d
from elisa.arch.sm import State, Transition, StateMachine
from sprites import SpriteMap, PSprite
import os
import pygame


class Elisa(pygame.sprite.Sprite):
    def __init__(self, sm: StateMachine, pos, **kwargs):
        super(Elisa, self).__init__()
        self._state_machine = sm
        self._current_animation_frame = 0
        self._current_state = sm.current.name
        self.can_walk_right, self.can_walk_left = True, True
        self._current_sprite = None
        self._assets = SpriteAssetManager()
        self._position = pos
        anims = ["WALK_RIGHT", "WALK_LEFT", "JUMP", "IDLE"]
        descfps = [
            "asset/elise_character/tileset_elisa_walk@8x.json",
            "asset/elise_character/tileset_elisa_walk@8x.json",
            "asset/elise_character/tileset_elisa_walk_jump@8x.json",
            "asset/elise_character/tileset_elisa_idle@8x.json",
        ]
        for key, fp in zip(anims, descfps):
            self._assets.add_sprite_map(name=key, metadata_fp=fp, verbose=True)
        self._sprites = {
            "Idle": self._assets.get_sprite(sprite_map_name="IDLE"),
            "Walk_Right": self._assets.get_sprite(sprite_map_name="WALK_RIGHT"),
            "Walk_Left": self._assets.get_sprite(sprite_map_name="WALK_LEFT"),
            "Jump": self._assets.get_sprite(sprite_map_name="JUMP"),
        }
        self._mirror_x = kwargs.get("mirror_x", False)
        self._mirror_y = kwargs.get("mirror_y", False)

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]

    @property
    def sprite_width(self):
        return self._current_sprite.width

    @property
    def sprite_height(self):
        return self._current_sprite.height

    def _right(self):
        if self.x >= 600:
            self.can_walk_left = False
        if self.can_walk_right:
            self._position = (self._position[0] + 3, self._position[1])

    def _left(self):
        if self._position[0] <= 100:
            self.can_walk_left = False
        if self.can_walk_left:
            self._position = (self._position[0] - 3, self._position[1])

    def update(self):
        self._state_machine.update()

        if self._state_machine.current.name != self._current_state:
            self._current_animation_frame = 0
            self._current_state = self._state_machine.current.name
        else:
            self._current_animation_frame += 1
            if (
                self._current_animation_frame
                >= self._sprites[self._current_state].no_sprites
            ):
                self._current_animation_frame = 0

        if self._current_state == "Walk_Right":
            self._right()
        elif self._current_state == "Walk_Left":
            self._left()
        else:
            pass

        self._current_sprite = self._sprites[self._current_state][
            self._current_animation_frame
        ]

    @property
    def rect(self):
        return pygame.Rect(
            self._position[0],
            self._position[1],
            self._current_sprite.width,
            self._current_sprite.height,
        )

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

    @property
    def image(self):
        s = self._current_sprite.image
        if self._mirror_x or self._mirror_y:
            s = pygame.transform.flip(s, self._mirror_x, self._mirror_y)
        return s


class SpriteAssetManager(object):
    """"""

    def __init__(self):
        """Constructor for AssetManager"""
        super(SpriteAssetManager, self).__init__()
        self._assets = {}

    def __repr__(self):
        return "Registered Assets ({}): {}".format(
            len(self._assets), self._assets.keys()
        )

    def add_sprite_map(
        self,
        name: str,
        metadata_fp: str,
        initialize: bool = True,
        verbose: bool = False,
    ):
        if not name:
            raise ValueError("name not provided")
        if not metadata_fp:
            raise ValueError("metadata file not provided")
        if name in self._assets:
            raise ValueError("asset already registered")
        if not os.path.exists(metadata_fp):
            raise ValueError("metadata file does not exist")

        if verbose:
            print("Adding Sprite Map: ", name)

        self._assets[name] = SpriteMap(metadata_fp)
        if initialize:
            self._assets[name].initialize(verbose=verbose)

    def get_sprite(self, sprite_map_name: str, sprite: str = None):
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

    def initialize(self, name: str = None):
        if not name:
            for a in self._assets:
                if not a.initialized:
                    a.initialize()
        else:
            if name not in self._assets:
                raise ValueError("not an asset")
            if not self._assets[name].initialized:
                self._assets[name].initialize()


def main():
    pygame.init()

    S_WIDTH = 800
    S_HEIGHT = 600
    S_TITLE = "Elisa 7 - Statemachine, GFX and pygame collision detection"

    C_WHITE = (255, 255, 255, 255)
    C_BLUE = (0, 0, 255, 255)
    C_RED = (255, 0, 0, 255)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    is_done = False

    key_map = pygame.key.get_pressed()
    fps_watcher = pygame.time.Clock()

    idle = State("Idle", "The idle state")
    s_final = State("Final", "Final State")
    walk_r = State("Walk_Right", "The walking state")
    walk_l = State("Walk_Left", "The walking state")

    jump = State("Jump", "The jumping state")

    t_idle_walk_left1 = Transition(
        idle,
        walk_l,
        trigger_fn=lambda: key_map[K_LEFT],
        name="IDLE_WALK_LEFT",
        description="From Idle to Walk Left",
    )
    t_idle_walk_left2 = Transition(
        idle, walk_l, lambda: key_map[K_a], "IDLE_WALK_LEFT", "From Idle to Walk Left"
    )
    t_idle_walk_right1 = Transition(
        idle,
        walk_r,
        trigger_fn=lambda: key_map[K_RIGHT],
        name="IDLE_WALK_RIGHT",
        description="From Idle to Walk Right",
    )
    t_idle_walk_right2 = Transition(
        idle,
        walk_r,
        trigger_fn=lambda: key_map[K_d],
        name="IDLE_WALK_RIGHT",
        description="From Idle to Walk Right",
    )

    t_walk_left_idle1 = Transition(
        walk_l,
        idle,
        trigger_fn=lambda: not key_map[K_LEFT],
        name="WALK_LEFT_IDLE",
        description="From Walk Left To Idle",
    )
    t_walk_left_idle2 = Transition(
        walk_l,
        idle,
        trigger_fn=lambda: not key_map[K_a],
        name="WALK_LEFT_IDLE",
        description="From Walk Left To Idle",
    )
    t_walk_right_idle1 = Transition(
        walk_r,
        idle,
        trigger_fn=lambda: not key_map[K_RIGHT],
        name="WALK_RIGHT_IDLE",
        description="From Walk Right To Idle",
    )
    t_walk_right_idle2 = Transition(
        walk_r,
        idle,
        trigger_fn=lambda: not key_map[K_d],
        name="WALK_RIGHT_IDLE",
        description="From Walk Right To Idle",
    )

    t_idle_jump1 = Transition(
        idle,
        jump,
        trigger_fn=lambda: key_map[K_UP],
        name="IDLE_JUMP",
        description="From Idle to Jump",
    )
    t_idle_jump2 = Transition(
        idle,
        jump,
        trigger_fn=lambda: key_map[K_w],
        name="IDLE_JUMP",
        description="From Idle to Jump",
    )
    t_jump_idle1 = Transition(
        jump,
        idle,
        trigger_fn=lambda: not key_map[K_UP],
        name="JUMP_IDLE",
        description="From Jump to Idle",
    )
    t_jump_idle2 = Transition(
        jump,
        idle,
        trigger_fn=lambda: not key_map[K_w],
        name="JUMP_IDLE",
        description="From Jump to Idle",
    )

    t_idle_final = Transition(
        idle,
        s_final,
        trigger_fn=lambda x=None: False,
        name="T_Idle_Final",
        description="Moving from idle to final",
    )

    states = [idle, walk_l, walk_r, jump, s_final]
    transitions1 = [
        t_idle_walk_left1,
        t_idle_walk_right1,
        t_idle_jump1,
        t_walk_left_idle1,
        t_walk_right_idle1,
        t_jump_idle1,
        t_idle_final,
    ]
    transitions2 = [
        t_idle_walk_left2,
        t_idle_walk_right2,
        t_idle_jump2,
        t_walk_left_idle2,
        t_walk_right_idle2,
        t_jump_idle2,
        t_idle_final,
    ]

    sm1 = StateMachine(
        states=states, transitions=transitions1, initial_state=idle, final_state=s_final
    )
    sm2 = StateMachine(
        states=states, transitions=transitions2, initial_state=idle, final_state=s_final
    )

    elisa1 = Elisa(sm=sm1, pos=(100, 100))
    # elisa2 faces elisa1 - so let's flip - small abuse so that instead of the original image
    # a mirrored image is returned, actually, we would do that once on sprite initialization and
    # avoid the cost on each frame, but this is simpler here
    elisa2 = Elisa(sm=sm2, pos=(400, 100), mirror_x=True)

    C_CLEAR = C_WHITE

    sprites = pygame.sprite.Group()
    sprites.add(elisa1)
    sprites.add(elisa2)

    while not is_done:
        fps_watcher.tick(16)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

            key_map = pygame.key.get_pressed()

        back_buffer.fill(C_CLEAR)

        sprites.update()

        if pygame.sprite.collide_rect(elisa1, elisa2):
            elisa1.can_walk_right = False
            elisa2.can_walk_left = False
        else:
            elisa1.can_walk_right = True
            elisa2.can_walk_left = True

        pygame.draw.rect(
            back_buffer,
            C_BLUE,
            (elisa1.x, elisa1.y, elisa1.sprite_width, elisa1.sprite_height),
            1,
        )
        pygame.draw.rect(
            back_buffer,
            C_RED,
            (elisa2.x, elisa2.y, elisa2.sprite_width, elisa2.sprite_height),
            1,
        )

        sprites.draw(back_buffer)
        screen_buffer.blit(back_buffer, (0, 0))

        pygame.display.flip()


if __name__ == "__main__":
    main()
