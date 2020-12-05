# auth: christian bitter
# name: elisa_7_sprite_animation.py
# desc: based on the previous elisa, we will now look into better definition of animation.

from pygame.locals import QUIT
import os
from elisa.sprite import SpriteSheet, SpriteAnimation
from elisa.arch.sm import State, StateMachine, Transition
import pygame


def trigger_idle_wl(key_func):
    def _trigger():
        return key_func()[pygame.K_LEFT]

    return _trigger


def trigger_idle_wr(key_func):
    def _trigger():
        return key_func()[pygame.K_RIGHT]

    return _trigger


def trigger_wl_idle(key_func):
    def _trigger():
        return not key_func()[pygame.K_LEFT]

    return _trigger


def trigger_wr_idle(key_func):
    def _trigger():
        return not key_func()[pygame.K_RIGHT]

    return _trigger


def idle_to_walk_fire(s_from, s_to):
    print("Now Walking")


def walk_to_idle_fire(s_from, s_to):
    print("Now idling")


def idle_to_final(s_from, s_to):
    print("In final")


def define_state_machine(key_func):
    # define states, transitions and build the state machine
    s_idle = State("Idle", "Elisa is in the idle state")
    s_walk_left = State("Walk_Left", "Elisa walks left")
    s_walk_right = State("Walk_Right", "Elisa walks right")
    s_final = State("Final", "The final state")
    t_idle_wl = Transition(
        s_idle,
        s_walk_left,
        trigger_idle_wl(key_func),
        idle_to_walk_fire,
        "T_Idle2WalkLeft",
        "transititioning from idle to walk left",
    )
    t_idle_wr = Transition(
        s_idle,
        s_walk_right,
        trigger_idle_wr(key_func),
        idle_to_walk_fire,
        "T_Idle2WalkRight",
        "transititioning from idle to walk right",
    )
    t_wl_idle = Transition(
        s_walk_left,
        s_idle,
        trigger_wl_idle(key_func),
        walk_to_idle_fire,
        "T_WalkLeft2Idle",
        "transitioning from walking left to idle",
    )
    t_wr_idle = Transition(
        s_walk_right,
        s_idle,
        trigger_wr_idle(key_func),
        walk_to_idle_fire,
        "T_WalkLeft2Idle",
        "transitioning from walking left to idle",
    )

    # final should not be reached
    t_idle_final = Transition(
        s_idle,
        s_final,
        lambda x=None: False,
        idle_to_final,
        "T_Idle_Final",
        "Moving from idle to final",
    )

    sm = StateMachine(
        [s_idle, s_walk_left, s_walk_right, s_final],
        [t_idle_wl, t_idle_wr, t_wl_idle, t_wr_idle, t_idle_final],
        s_idle,
        s_final,
    )
    val_result, val_reason = sm.validate()
    if not val_result:
        raise ValueError("Validated State Machine: {}".format(val_reason))
    return sm


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    # init pygame - create the main window, and a background surface
    pygame.init()
    elisa_sm = define_state_machine(pygame.key.get_pressed)

    S_WIDTH = 640
    S_HEIGHT = 480
    S_TITLE = "Elisa - Statemachine and GFX"

    C_WHITE = (250, 250, 250)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    anim_sheet = SpriteSheet("asset/elise_character/tileset_elisa@2x.json")
    anim_sheet.initialize(verbose=False)
    idle_anim = SpriteAnimation(
        name="Elisa_idle", sprite_sheet=anim_sheet, fps=24, repeats=True
    )
    idle_anim = (
        idle_anim.add_frame("idle_1")
        .add_frame("idle_2")
        .add_frame("idle_3")
        .add_frame("idle_4")
    )
    walk_anim = SpriteAnimation(
        name="Elisa_walk",
        sprite_sheet=anim_sheet,
        fps=24,
        repeats=True,
        frames=["walk_1", "walk_2", "walk_3", "walk_4", "walk_5", "walk_6"],
    )

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    # FPS watcher
    fps_watcher = pygame.time.Clock()
    is_done = False

    sprite_x, sprite_y = 100, 100

    current_anim = idle_anim

    while not is_done:
        _elapsed_ms = fps_watcher.tick(24)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

        previous = elisa_sm.current

        elisa_sm.update()

        if elisa_sm.current != previous:
            # before we update the animation, we reset
            current_anim.reset()
            if elisa_sm.current.name == "Idle":
                current_anim = idle_anim
            elif (
                elisa_sm.current.name == "Walk_Left"
                or elisa_sm.current.name == "Walk_Right"
            ):
                current_anim = walk_anim
            else:
                raise ValueError("Unknow state transitioned into")

        back_buffer.fill(C_WHITE)
        back_buffer.blit(
            current_anim.update(_elapsed_ms).as_pygame_sprite, (sprite_x, sprite_y)
        )
        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main()
