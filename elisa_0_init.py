# name: elisa_0_init.py
# auth: (c) 2020 christian bitter
# desc: based off our template we are going to explore the initialization process

import pygame

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

	if not pygame.font:
		print("Pygame - fonts not loaded")
	if not pygame.mixer:
		print("Pygame - audio not loaded")
	if not pygame.display:
		print("Pygame - display not loaded")
	if not pygame.mouse:
		print("Pygame - mouse not loaded")

	print("Did we initialize: {}".format(pygame.get_init()))
	print("Pygame Version: {}".format(pygame.ver))
	print("Pygame runs on SDL Version: {}".format(pygame.get_sdl_version()))
	print("Pygame Display Driver: {}".format(pygame.display.get_driver()))
	
	# for pontential cleanup of other resources, we register a quit handler. This handler will be invoked whenever
	# pygame enters the quit state.
	pygame.register_quit(on_quit)

	w, h, t = 640, 480, "Elisa - 0 Pygame Initialization"
	c_white = (255, 255, 255)

	# here we create a display surface of width and height: https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
	# we have different options to create a display surface, such as enabling double buffering, preparing it for opengl
	# removing borders or going full screen. However, we will not do any of this, by using the flags=0
	# this will create a default software rasterizer supported window of size, no full screen and default layout.
	# Setting the display mode will also return a buffer object/ pixel surface, that we can draw to.
	# then we set the window's caption and icon title (for shorter displays)
	# Then we make the mouse cursor visible
	screen_buffer = pygame.display.set_mode(size=(w, h), flags=0)
	pygame.display.set_caption(t, "Elisa 0")
	pygame.mouse.set_visible(True)

	# the next lines are concerned with supporting a double-buffered drawing approach.
	# in double-buffered drawing one does not draw to the display surface directly, in order to avoid drawing/ refresh issues.
	# instead one draws to a back buffer and when time comes then the image fully drawn to the back buffer will be copied to the displayed
	# front buffer. 
	# 
	# So we setup a back buffer, that matches our visible screen buffer in size, and for the time being clear it with white color.
	# Later on, we constantly copy (blit) our back buffer to the front buffer associated with the display and then flip, such 
	# what is drawn to the back buffer becomes visible to our eyes - for the time being only a white canvas.
	back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
	back_buffer = back_buffer.convert()
	back_buffer.fill(c_white)

	# here we setup a pygamer clock - we will discuss this in a later example
	fps_watcher = pygame.time.Clock()
	is_done = False

	# Now, we are ready to setup our game loop, where we loop until our application/ game is done - then we break from the loop.
	# As you can see, there is only condition that exits from the loop - and that is when the application receives a QUIT event message.
	# One way to receive this message is by clicking the closing button of the window. 
	# Another way is to send ctrl+c in the console window.
	while not is_done:
		elapsed_millis = fps_watcher.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				is_done = True
				break

		if not is_done:
			screen_buffer.blit(back_buffer, (0, 0))
			pygame.display.flip()

	# after exiting the loop we call it Quit - this will invoke our Quit handler and we are free to perform any heavy clean up lifting
	# such as freeing memory or releasing any other resources
	pygame.quit()

if __name__ == '__main__':
	main()
