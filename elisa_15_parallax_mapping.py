# auth: christian bitter
# name: elisa_15_parallax_mapping
# desc: a simple parallax mapping example ...
#       we load the layers of a parallax mapped background separately
#       the arrow keys allow going left and right
# vers: 0.1

# TODO: scale the images up-front to the screen size

import pygame
import os, sys
from elisa.sprite import load_png, Sprite, SpriteAnimation, SpriteSheet
from elisa.arch.sm import State, StateMachine, Transition

def load_images(target_width: int = 640, target_height: int = 480, verbose:bool=False):
    img_container = {}
    ckey = (255, 255, 255, 0)
    img_base_path = "asset/gfx/raventale_parallax_backgound_scaled"

    # all images have the same size - 2048x1546 - we will scale them back
    for img_name in os.listdir(img_base_path):
        if not img_name.endswith('.png'):
            continue
        image_fp = os.path.join(img_base_path, img_name)
        img = load_png(image_fp, image_only=True)
        img = pygame.transform.scale(img, (target_width, target_height))
        img_container[img_name] = img

    if verbose:
        print("Loaded {} images ...".format(len(img_container)))

    img_order = [
        '_11_background.png',
        '_10_distant_clouds.png',
        '_09_distant_clouds1.png',
        '_08_clouds.png',
        '_07_huge_clouds.png',
        '_05_hill1.png',
        '_06_hill2.png',
        '_04_bushes.png',
        '_03_distant_trees.png',
        '_02_trees and bushes.png',
        '_01_ground.png'
    ]

    img_layer_speed = {
        '_11_background.png' : 3,
        '_10_distant_clouds.png' : 4,
        '_09_distant_clouds1.png': 5,
        '_08_clouds.png': 6,
        '_07_huge_clouds.png': 8,
        '_05_hill1.png': 10,
        '_06_hill2.png': 11,
        '_04_bushes.png': 12,
        '_03_distant_trees.png': 13,
        '_02_trees and bushes.png': 14,
        '_01_ground.png': 20
    }

    return img_container, img_order, img_layer_speed


# we simply copy the state machine from elisa7
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
	#define states, transitions and build the state machine
	s_idle = State('Idle', 'Elisa is in the idle state')
	s_walk_left = State('Walk_Left', 'Elisa walks left')
	s_walk_right = State('Walk_Right', 'Elisa walks right')
	s_final      = State('Final', 'The final state')
	t_idle_wl = Transition(s_idle, s_walk_left, trigger_idle_wl(key_func), idle_to_walk_fire, 'T_Idle2WalkLeft', 'transititioning from idle to walk left')
	t_idle_wr = Transition(s_idle, s_walk_right, trigger_idle_wr(key_func), idle_to_walk_fire, 'T_Idle2WalkRight', 'transititioning from idle to walk right')
	t_wl_idle = Transition(s_walk_left, s_idle, trigger_wl_idle(key_func), walk_to_idle_fire, 'T_WalkLeft2Idle', 'transitioning from walking left to idle')
	t_wr_idle = Transition(s_walk_right, s_idle, trigger_wr_idle(key_func), walk_to_idle_fire, 'T_WalkLeft2Idle', 'transitioning from walking left to idle')
	
	# final should not be reached
	t_idle_final = Transition(s_idle, s_final, lambda x=None: False, idle_to_final, 'T_Idle_Final', 'Moving from idle to final')

	sm = StateMachine([s_idle, s_walk_left, s_walk_right, s_final],
										[t_idle_wl, t_idle_wr, t_wl_idle, t_wr_idle,
										t_idle_final],
										s_idle, s_final)
	val_result, val_reason = sm.validate()
	if not val_result:
		raise ValueError("Validated State Machine: {}".format(val_reason))
	return sm

def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    elisa_sm = define_state_machine(pygame.key.get_pressed)

    pygame.init()

    w, h, t = 640, 480, "Elisa - 15 Parallax Mapping"
    c_white = (255, 255, 255)
    c_black = (0, 0, 0, 255)

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    anim_sheet   = SpriteSheet("asset/elise_character/tileset_elisa@2x.json")
    anim_sheet.initialize(verbose=False)    
    idle_anim    = SpriteAnimation(name="Elisa_idle", sprite_sheet=anim_sheet, fps=24, repeats=True)
    idle_anim    = idle_anim.add_frame("idle_1").add_frame("idle_2").add_frame("idle_3").add_frame("idle_4")		
    walk_anim    = SpriteAnimation(name="Elisa_walk", sprite_sheet=anim_sheet, fps=24, repeats=True, frames=["walk_1", "walk_2", "walk_3", "walk_4", "walk_5", "walk_6"])    

    # we make the target width slightly larger
    img_width, img_height = 2*w, h
    layers, layer_ordering, layer_speed = load_images(target_width=img_width, target_height=img_height)

    # for each of the images .. we define a parallax order
    # we assume that the first layer is the farthest away.

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size(), pygame.SRCALPHA)
    img_surface = pygame.Surface(screen_buffer.get_size(), pygame.SRCALPHA)

    # back_buffer = back_buffer.convert()
    back_buffer.fill(c_black)

    fps_watcher = pygame.time.Clock()
    is_done = False
    w2 = w // 2
    h2 = h // 2
    speed = 10
    x_dir = 0
    
    # initially all pictures are aligned to the same x-pos, but over time we make them shift gradually
    player_x = 320
    x_pos = [320] * len(layers)

    sprite_x, sprite_y = player_x, 350
    current_anim = idle_anim

    while not is_done:
        elapsed_millis = fps_watcher.tick(60)
        x_dir = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break
            else:
                key_pressed = pygame.event == pygame.KEYDOWN
                key_map = pygame.key.get_pressed()

        previous = elisa_sm.current

        elisa_sm.update()

        if elisa_sm.current != previous:
            # before we update the animation, we reset
            current_anim.reset()
            if elisa_sm.current.name == 'Idle':
                current_anim = idle_anim
            elif elisa_sm.current.name == 'Walk_Left' or elisa_sm.current.name == 'Walk_Right':
                current_anim = walk_anim
            else:
                raise ValueError("Unknow state transitioned into")

        if key_map[pygame.K_LEFT]:
            x_dir = -1
        if key_map[pygame.K_RIGHT]:
            # shift the area
            x_dir = 1

        # we calculate the viewing window, as the half to the left and half to the right
        # if we go the the outside of the image, we need to add images back at the end        
        # since every layer can move at different speeds, we will have different viewing windows at every layer
        # for now we fix the speed upfront
        for i, lo in enumerate(layer_ordering):
            lspeed = layer_speed[lo]
            x_pos[i] = x_pos[i] + x_dir * lspeed
        
        back_buffer.fill(c_black)
        for i, lo in enumerate(layer_ordering):
            l = layers[lo]
            l_xpos = x_pos[i]            
            # if our window is outside of the blitting surface, we stich it together
            xmin, xmax = (l_xpos - w2), (l_xpos + w2)
            
            if 0 <= xmin <= img_width and 0 <= xmax <= img_width:
                back_buffer.blit(l, (0,0), area=[xmin, 0, xmax, h])
            elif xmin >= img_width:
                x_pos[i] = w2
                xmin = 0
                xmax = w                
                back_buffer.blit(l, (0, 0), area=[xmin, 0, xmax, h])
            elif xmin < 0 and xmax <= 0:
                x_pos[i] = w2
                xmin = 0
                xmax = w
                back_buffer.blit(l, (0, 0), area=[xmin, 0, xmax, h])
            elif xmin < 0:
                # partial blitting
                abs_xmin = abs(xmin)
                back_buffer.blit(l, (0, 0), [img_width - abs_xmin, 0, abs_xmin, h])
                back_buffer.blit(l, (abs_xmin, 0), [0, 0, xmax, h])
            else:
                # partial blitting
                back_buffer.blit(l, (0, 0), [xmin, 0, img_width, h])
                back_buffer.blit(l, (img_width - xmin, 0), [0, 0, xmax - img_width, h])

        back_buffer.blit(current_anim.update(elapsed_millis).as_pygame_sprite, (sprite_x, sprite_y))

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    main()
