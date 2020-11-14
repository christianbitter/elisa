# auth: christian bitter
# name: elisa_8_-_tilemap.py
# desc: 
# In this example, we take what we learnt in elisa_6_environment_map and elisa_7_sprite_animation to create
# a more lifely environment. We are going to follow the examples from Mozilla somewhat closely. By separating the tile map
# definition from its rendering process, we can easily swap different visuals in and out. For example, if you do not like the
# 3 tiles we used here, you may simply instantiate a different sprite sheet.
# Our simplistic renderer combines the camera portion with the actual surface handling. This clearly is not ideal and will be
# removed at a future point in time. In order to be somewhat mindful of our resources, we do not render anything outside of the visible
# parts of the screen. In order to make the environment appear a tiny bit more inhabited, we added the elise sprite waiting idly.
# Please note, that there is no sophisticated collision detection implemented right now, so you can easily bump into elise.

# asset credit: Mozilla and https://developer.mozilla.org/en-US/docs/Games/Techniques/Tilemaps
# asset credit: Elise Sprite TODO:
# in order to create tile sets, you may find the following helpful:
# sprite packing: https://www.leshylabs.com/apps/sstool/

import os
import pygame
from pygame.locals import *
from elisa.sprite import Tile, TileMap, SpriteSheet, Sprite, SpriteAnimation
from elisa.arch.sm import State, StateMachine, Transition
import json

def trigger_idle_wl(key_func):
	def _trigger():		
		return key_func()[pygame.K_LEFT]
	return _trigger

def trigger_idle_wu(key_func):
	def _trigger():		
		return key_func()[pygame.K_UP]
	return _trigger

def trigger_idle_wd(key_func):
	def _trigger():		
		return key_func()[pygame.K_DOWN]
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

def trigger_wu_idle(key_func):
	def _trigger():
		return not key_func()[pygame.K_UP]
	return _trigger

def trigger_wd_idle(key_func):
	def _trigger():		
		return not key_func()[pygame.K_DOWN]
	return _trigger

def idle_to_walk_fire(s_from, s_to):
	pass

def walk_to_idle_fire(s_from, s_to):
	pass

def define_state_machine(key_func):
	#define states, transitions and build the state machine
	s_idle = State('Idle', 'Character is in the idle state')
	s_walk_left  = State('Walk_Left', 'Character walks left')
	s_walk_right = State('Walk_Right', 'Character walks right')
	s_walk_up    = State('Walk_Up', 'Character walks up')
	s_walk_down  = State('Walk_Down', 'Character walks down')

	t_idle_wl = Transition(s_idle, s_walk_left, trigger_idle_wl(key_func), idle_to_walk_fire, 'T_Idle2WalkLeft', 'transititioning from idle to walk left')
	t_idle_wr = Transition(s_idle, s_walk_right, trigger_idle_wr(key_func), idle_to_walk_fire, 'T_Idle2WalkRight', 'transititioning from idle to walk right')
	t_idle_wu = Transition(s_idle, s_walk_up, trigger_idle_wu(key_func), idle_to_walk_fire, 'T_Idle2WalkUp', 'transititioning from idle to walk up')
	t_idle_wd = Transition(s_idle, s_walk_down, trigger_idle_wd(key_func), idle_to_walk_fire, 'T_Idle2WalkDown', 'transititioning from idle to walk down')

	t_wl_idle = Transition(s_walk_left, s_idle, trigger_wl_idle(key_func), walk_to_idle_fire, 'T_WalkLeft2Idle', 'transitioning from walking left to idle')
	t_wr_idle = Transition(s_walk_right, s_idle, trigger_wr_idle(key_func), walk_to_idle_fire, 'T_WalkLeft2Idle', 'transitioning from walking left to idle')
	t_wu_idle = Transition(s_walk_up, s_idle, trigger_wu_idle(key_func), walk_to_idle_fire, 'T_WalkUp2Idle', 'transitioning from walking up to idle')
	t_wd_idle = Transition(s_walk_down, s_idle, trigger_wd_idle(key_func), walk_to_idle_fire, 'T_WalkDown2Idle', 'transitioning from walking down to idle')

	sm = StateMachine([s_idle, s_walk_left, s_walk_right, s_walk_up, s_walk_down],
					  [t_idle_wl, t_idle_wr, t_wl_idle, t_wr_idle, t_idle_wu, t_idle_wd, t_wu_idle, t_wd_idle],
					  s_idle)
	return sm

def define_elise_sm():
	s_idle = State('Idle', 'Character is in the idle state')

	sm = StateMachine([s_idle], [], s_idle)

	return sm

class TileMapRenderer(object):
	C_WHITE = (255, 255, 255)

	def __init__(self, tile_map:TileMap, tile_atlas:SpriteSheet, world_x:int, world_y:int, view_width:int, view_height:int):
		super(TileMapRenderer, self).__init__()
		if not tile_map:
			raise ValueError("Tile map not provided")
		if not tile_atlas:
			raise ValueError("Tile Atlas not provided")
		if not tile_atlas.initialized:
			raise ValueError("Tile Atlas not initialized")
		if not 'GFX' in tile_map:
			raise ValueError("No renderable map presented")

		self._tile_map = tile_map
		self._tile_atlas = tile_atlas
		self._index2sprite = {
			0: None,
			1: "grass_1",
			2: "mud_1",
			3: "tree_1"
		}

		self._clear_colour = TileMapRenderer.C_WHITE

		self._tile_width = self._tile_map.tile_dimension[0]
		self._tile_height= self._tile_map.tile_dimension[1]

		self._empty_tile = pygame.surface.Surface(self._tile_map.tile_dimension)
		self._view_width = view_width
		self._view_height = view_height
		self._x = world_x
		self._y = world_y

	def clear_buffer(self, surface):
		surface.fill(self._clear_colour)

	def render(self, surface):
		self.clear_buffer(surface)        
		
		_x0, _y0 = self._x, self._y
		
		for y in range(self._tile_map.map_height):
			_x0 = self._x

			# very primitive do not render anything strictly outside of the visible bounds
			if _y0 >= self._view_height or _x0 >= self._view_width:
				next

			for x in range(self._tile_map.map_width):
				ti = self._tile_map.get_tile_index("GFX", x, y)
				ta_i = self._index2sprite[ti]
				if not ta_i:
					# this should be the empty tile
					tile_i = self._empty_tile
				else:
					tile_i:Sprite = self._tile_atlas[ta_i].as_pygame_sprite
				surface.blit(tile_i, (_x0, _y0))
				_x0 += self._tile_width
			_y0 += self._tile_height

def build_world():
	world_map = [
		[1, 3, 3, 3, 1, 1, 3, 1],
		[1, 1, 1, 1, 1, 1, 1, 1],
		[1, 1, 1, 1, 1, 2, 1, 1],
		[1, 1, 1, 1, 1, 1, 1, 1],
		[1, 1, 1, 2, 1, 1, 1, 1],
		[1, 1, 1, 1, 2, 1, 1, 1],
		[1, 1, 1, 1, 2, 1, 1, 1],
		[1, 1, 1, 0, 0, 1, 1, 1]
	]
	tm = TileMap(tile_extent=64, map_width=8, map_height=8)
	tm.add_grid(grid_name='GFX', data=world_map)
	return tm

def main():
	pygame.init()

	character_sm = define_state_machine(pygame.key.get_pressed)
	elise_sm     = define_elise_sm()

	MAP_OFFSET_X, MAP_OFFSET_Y = 50, 50
	MOVE_SPEED_HORIZONTAL, MOVE_SPEED_VERTICAL = 3, 3

	C_WHITE = (255, 255, 255)
	S_WIDTH = 800
	S_HEIGHT= 600
	S_TITLE = "Elisa 8 - Tilemap"

	screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
	pygame.display.set_caption(S_TITLE)
	pygame.mouse.set_visible(True)

	world:TileMap = build_world()
	sheet = SpriteSheet.create(json_descriptor_fp="asset/tile_map_mozilla/tileset_tiles.json")    
	tm_renderer = TileMapRenderer(world, sheet, world_x=MAP_OFFSET_X, world_y=MAP_OFFSET_Y, view_width=S_WIDTH, view_height=S_HEIGHT)

	anim_sheet   = SpriteSheet.create(json_descriptor_fp="asset/tile_map_mozilla/tileset_character.json")
	idle_anim    = SpriteAnimation(name="Character_idle", sprite_sheet=anim_sheet, fps=24, repeats=True, frames=["main"])
	walk_anim    = SpriteAnimation(name="Character_walk", sprite_sheet=anim_sheet, fps=24, repeats=True, frames=["main"])

	elise_sheet  = SpriteSheet.create(json_descriptor_fp="asset/elise_character/tileset_elisa@2x.json")
	e_idle_anim  = SpriteAnimation(name="Elise_idle", sprite_sheet=elise_sheet, fps=24, repeats=True, frames=["idle_1", "idle_2", "idle_3", "idle_4"])

	back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
	back_buffer = back_buffer.convert()
	back_buffer.fill(C_WHITE)

	fps_watcher = pygame.time.Clock()
	is_done = False

	sprite_x, sprite_y = MAP_OFFSET_X, MAP_OFFSET_Y
	elise_x, elise_y   = 300, 300

	current_anim       = idle_anim;
	current_elise_anim = e_idle_anim

	while not is_done:
		_elapsed_ms = fps_watcher.tick(24)

		for event in pygame.event.get():
			if event.type == QUIT:
				is_done = True
				break

		previous = character_sm.current
		character_sm.update()
		elise_sm.update()

		if character_sm.current != previous:
		# before we update the animation, we reset
			current_anim.reset()
			if character_sm.current.name == 'Idle':
				current_anim = idle_anim
			else:
				current_anim = walk_anim

		# now walk - notice that due to our non-integral movement update, it might be that the player ends up
		# on or slightly outside of the bounds of the world
		if character_sm.current.name == 'Walk_Left' and sprite_x > MAP_OFFSET_X:
			sprite_x -= MOVE_SPEED_HORIZONTAL
		elif character_sm.current.name == 'Walk_Right' and sprite_x < MAP_OFFSET_X + (world.map_width - 1) * world.tile_width:
			sprite_x += MOVE_SPEED_HORIZONTAL
		elif character_sm.current.name == 'Walk_Up'  and sprite_y > MAP_OFFSET_Y:
			sprite_y -= MOVE_SPEED_VERTICAL
		elif character_sm.current.name == 'Walk_Down' and sprite_y < MAP_OFFSET_Y + (world.map_height - 1) * world.tile_height:
			sprite_y += MOVE_SPEED_VERTICAL
		else:
			pass

		tm_renderer.render(back_buffer)
		back_buffer.blit(current_anim.update(_elapsed_ms).as_pygame_sprite, (sprite_x, sprite_y))
		back_buffer.blit(current_elise_anim.update(_elapsed_ms).as_pygame_sprite, (elise_x, elise_y))
		screen_buffer.blit(back_buffer, (0, 0))
		pygame.display.flip()

if __name__ == '__main__': main()
