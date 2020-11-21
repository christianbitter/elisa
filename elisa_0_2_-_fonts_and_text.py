# name: elisa_0_2_-_fonts_and_text.py
# auth: (c) 2020 christian bitter
# desc: draw text of different sizes with different visual attributes set
import os
import sys
import pygame
from random import randint, random
from time import sleep

C_BLACK = (0, 0, 0)

def on_quit():
	print("Elisa -> Quit()")

def main():
	# init is a convenient way to initialize all subsystems
	# instead we could also initialize the submodules directly - for example by calling pygame.display.init(), pygame.display.quit()
	no_pass, no_fail = pygame.init()

	if no_fail > 0:
		print("Not all pygame modules initialized correctly")
		print(pygame.get_error())
	else:
		print("All pygame modules initializes")

	# in order to actually do something with text, we need to ensure that the font module is initialized. Furthermore, since we want to
	# draw some text to the screen it makes sense to also check the display initialization.
	if not pygame.font:
		print("Pygame - fonts not loaded")
	if not pygame.display:
		print("Pygame - display not loaded")

	print("Did we initialize: {}".format(pygame.get_init()))
	print("Pygame Version: {}".format(pygame.ver))
	print("Pygame runs on SDL Version: {}".format(pygame.get_sdl_version()))
	print("Pygame Display Driver: {}".format(pygame.display.get_driver()))
	
	# for pontential cleanup of other resources, we register a quit handler. This handler will be invoked whenever
	# pygame enters the quit state.
	pygame.register_quit(on_quit)

	w, h, t = 640, 480, "Elisa - 0.2 Fonts and Text"
	c_white = (255, 255, 255)

	screen_buffer = pygame.display.set_mode(size=(w, h), flags=0)
	pygame.display.set_caption(t, "Elisa 0.2")
	pygame.mouse.set_visible(True)

	back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
	back_buffer = back_buffer.convert()
	back_buffer.fill(c_white)

	# here we setup a pygamer clock - we will discuss this in a later example
	fps_watcher = pygame.time.Clock()
	is_done = False

	# let's see which fonts we do have
	fonts = pygame.font.get_fonts()
	no_fonts = len(fonts)

	print("Found {} fonts ...".format(no_fonts))
	for i, f in enumerate(fonts):
		print("Found font: ", f)

	while not is_done:
		elapsed_millis = fps_watcher.tick(16)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				is_done = True
				break

		# clear the screen and write something in a randomly coloured, random font
		back_buffer.fill(C_BLACK)		

		c = (randint(0, 255), randint(0, 255), randint(0, 255))
		x, y = randint(100, 500), randint(50, 450)
		i_font = randint(0, no_fonts - 1)
		size   = randint(20, 50)
		# while get_fonts returned a list of all fonts on the system, sometimes they may not be system fonts and
		# directly referencable by pygame, that is why we call match font here, which
		# if the font is installed on the system gives us the path to the font - still then it seems in certain cases
		# is not really present on the system, so we include another check
		font = pygame.font.match_font(fonts[i_font])
		if not os.path.exists(font):
			print("Font does not exist: ", font)
			continue
		
		f = pygame.font.Font(font, size)		

		# now, let's flip some coins in order to add text effects like bold, italic or underlining
		if random() >= .5:
			f.set_bold(True)
		if random() >= .5:
			f.set_italic(True)
		if random() >= .5:
			f.set_underline(True)

		# Note that the text can only be a single line, font render returns a surface that we can blit into our
		# main surface. Here, we set antialiasing to false
		text = f.render("Hello", False, c)
		
		back_buffer.blit(text, (x, y))
		
		if not is_done:
			screen_buffer.blit(back_buffer, (0, 0))
			pygame.display.flip()

		sleep(.5)

	pygame.quit()

if __name__ == '__main__':
	main()