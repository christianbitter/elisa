# auth: christian bitter
# desc: in this tutorial we are going to develop a simple state machine.
#       the state machine registers simple-named states like walk, jump, idle.
#       when you press the arrow keys right or up, the machine transitions from
#       idle to a moving state like jump or walk. after that the machine transitions back to idle.

import pygame
from pygame.locals import *
import uuid


class State(object):
    def __init__(self, name:str, description:str = None):
        super(State, self).__init__()

        self._id   = uuid.uuid1()
        self._name = name
        self._description = description

    def __repr__(self):
        return "{} ({})".format(self._name, self._id)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __eq__(self, other):
        return other.id == self._id


class Transition(object):
    def __init__(self, f: State, t: State, trigger_fn, name: str = None, description: str = None):
        super(Transition, self).__init__()
        self._id = uuid.uuid1()
        self._from = f
        self._to = t
        self._trigger = trigger_fn
        self._name = name
        self._description = description

    def __repr__(self):
        return "{} ({}) : {} => {}".format(self._id, self._name, self._from, self._to)

    def fires(self) -> bool:
        return self._trigger()

    @property
    def from_state(self):
        return self._from

    @property
    def to_state(self):
        return self._to


class StateMachine(object):

    def __init__(self, states: list, transitions: list, initial_state: State):
        self._id   = uuid.uuid1()
        self._init = initial_state
        self._current_state = self._init
        self._states = states.copy()
        self._transitions = transitions.copy()

        # self._validate()

    def _validate(self):
        raise ValueError("TODO:")

    @property
    def current(self):
        return self._current_state

    def update(self):
        # get the transitions for the current state, call fires and see ...
        # in order to be deterministic we allow only a single firing transition, although we allow multiple transitions
        # per state - but this is the job of the validate function
        firing_transition = None
        for t in self._transitions:
            if t.from_state == self._current_state:
                if t.fires():
                    firing_transition = t
                    break

        if firing_transition:
            self._current_state = firing_transition.to_state


def main():
    if not pygame.font: print("Pygame - fonts not loaded")
    if not pygame.mixer: print("Pygame - audio not loaded")

    # init pygame - create the main window, and a background surface
    pygame.init()

    S_WIDTH = 800
    S_HEIGHT= 600
    S_TITLE = "PyBlocks"

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
    textpos.centery = back_buffer.get_rect().centery - 18


    key_map = pygame.key.get_pressed()
    pressed = False

    idle = State("Idle", "The idle state")
    walk = State("Walk", "The walking state")
    jump = State("Jump", "The jumping state")

    def idle_to_walk():
        return key_map[K_RIGHT]

    def idle_to_jump():
        return key_map[K_UP]

    def jump_to_idle():
        return not key_map[K_UP]

    def walk_to_idle():
        return not key_map[K_RIGHT]

    t_idle_walk = Transition(idle, walk, idle_to_walk, "IDLE_WALK", "From Idle to Walk")
    t_walk_idle = Transition(walk, idle, walk_to_idle, "WALK_IDLE", "From Walk To Idle")
    t_idle_jump = Transition(idle, jump, idle_to_jump, "IDLE_JUMP", "From Idle to Jump")
    t_jump_idle = Transition(jump, idle, jump_to_idle, "JUMP_IDLE", "From Jump to Idle")

    sm = StateMachine(states=[idle, walk, jump],
                      transitions=[t_idle_walk, t_idle_jump, t_walk_idle, t_jump_idle],
                      initial_state=idle)

    while not is_done:
        fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

            key_map = pygame.key.get_pressed()

        sm.update()
        text = font.render("Current State: {}".format(sm.current), 1, C_BLUE)
        back_buffer.fill(C_WHITE)
        back_buffer.blit(text, textpos)
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()
