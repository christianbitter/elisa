# auth: christian bitter
# name: elisa_11_sounds.py
# desc: play a sound
#   whenever the mouse button is pressed, we play the sound
#   when the user releases the mouse button the sound is stopped
#   when you continuously hold the mouse button, the sound will be re-played after it has ended.
# audio: Beam.mp3 by Kastenfrosch
#   converted to ogg using https://www.online-convert.com/
# downloaded from free sound here: https://freesound.org/people/Kastenfrosch/sounds/162479/
# requires pygame 1.8 for mixer.Sound

import os
import pygame


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - mixer not loaded")

    # init pygame - create the main window, and a background surface

    pygame.init()

    S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Elisa - Play a sound"
    C_WHITE = (255, 255, 255)

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(C_WHITE)

    # FPS watcher
    fps_watcher = pygame.time.Clock()
    is_done = False

    sound_fp = "asset/sound/162479__kastenfrosch__beam.ogg"
    if not sound_fp or not os.path.exists(sound_fp):
        raise ValueError("You are missing 162479__kastenfrosch__beam")

    sound = pygame.mixer.Sound(sound_fp)
    sound_length = sound.get_length() * 1e3
    print("The effect is {} milli-seconds long".format(sound_length))
    elapsed_sound_time = 0
    mouse_down, sound_playing = False, False

    font = pygame.font.Font(None, 32)
    text = [
        font.render("Press (and hold) any mouse button", 1, (0, 64, 192, 255)),
        font.render("to trigger the playing of the sound", 1, (0, 64, 192, 255)),
    ]

    while not is_done:
        fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
            else:
                pass

        if mouse_down and not sound_playing:
            sound_playing = True
            sound.play()
        elif not mouse_down and sound_playing:
            sound_playing = False
            elapsed_sound_time = 0
            sound.stop()
        elif mouse_down and sound_playing:
            elapsed_sound_time += fps_watcher.get_time()
            if elapsed_sound_time >= sound_length:
                print(
                    "we played the full track - let's restart since you like it so much ..."
                )
                elapsed_sound_time = 0
                sound_playing = False
        else:
            pass

        x0, y0 = 300, 200
        for f in text:
            back_buffer.blit(f, (x0 - (f.get_width() / 2), y0))
            y0 += f.get_height()

        screen_buffer.blit(back_buffer, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main()
