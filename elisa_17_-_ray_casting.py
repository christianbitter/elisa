# name: elisa_17_-_ray_casting.py
# auth: (c) 2020 christian bitter
# desc:
# this example is about a player in a 2D world where visibility of world elements is determined using
# ray-casting. We place some random visual obstables (boxes) into this world to demonstrate the ray casting.
# Actual visibility will not be decided using the ray casting, instead we will highlight those entities that would lie in the
# field of view of our player. The field of view is defined by some opening angle and a viewing distance. This forms a triangle.
# All points inside of this triangle are visible to the player. As opposed to a contained visibility test, we perform the
# ray casting visibility test, i.e. we sample the field of view using rays emanating from the player's position in the viewing
# direction contained in the field of view. Now, whenever we have a ray hit an object, that object is visible. In such a case, the
# ray hitting the object and the actual object are highlighted.
# We build on the previously introduced entity-component system. That is, we will define
# entities for the movable player and the boxes. Also, properties defined in components make up the speific
# configurations of these entities. Two systems will be defined the rendering system and the input handling system.
# This may not be an optimal ECS but it demonstrates the decompositioning of our demanded functionality.
# You can move the player via the arrow keys and alternatively via W-A-S-D

# NOTE: For a future version/ expanded tutorial, we should use the camera introduced earlier.

import enum
from math import pi, sin, cos
import pygame
from elisa.arch.ecs import Entity, Component, Message, System
from elisa import Point2, Vec2, Point2
import elisa.linalg
from elisa.linalg import Ray2, Plane2

# Let us define a couple of types
# the player entity
# a position and directional velocity component
# a system to handle input
# a system to handle rendering
# and a couple of messages

class EPlayer(Entity):
	def __init__(self):
		super(EPlayer, self).__init__()

	def handle_position_update(self, delta_pos:Vec2):
		pos = self._ctypes["Transform2"].position
		self._ctypes["Transform2"].position = pos + delta_pos

	def handle_orientation_update(self, delta_angle:float):
		orientation = self._ctypes["Transform2"].viewing_direction
		rorientation = orientation.to_angle() % (pi*2.)
		aorientation= elisa.linalg.rad_to_angle(rorientation)
		s_angle     = 1. if delta_angle >= 0 else -1.
		aorientation= aorientation + s_angle * elisa.linalg.rad_to_angle(abs(delta_angle))
		aorientation= aorientation % 360.		
		orientation = elisa.linalg.angle_to_rad(aorientation)
		self._ctypes["Transform2"].viewing_direction = Vec2.from_angle(orientation)

	def send_msg(self, msg:Message):
		if msg.message_type == 'UpdatePosition':
			dpos = msg.delta_position
			self.handle_position_update(dpos)
		elif msg.message_type == 'UpdateOrientation':
			dangle = msg.delta_orientation
			self.handle_orientation_update(dangle)

class EBox(Entity):
	def __init__(self):
		super(EBox, self).__init__()

class Shape(enum.Enum):
	Point = 1
	Square = 2

class CRenderable(Component):
	def __init__(self, render_color=(255, 255, 255), shape = Shape.Point, width=None):
		super(CRenderable, self).__init__("Renderable")
		self._render_color = render_color
		self._shape        = shape
		self._width        = width

	@property
	def color(self):
		return self._render_color

	@property
	def shape(self):
		return self._shape

	@property
	def width(self):
		return self._width

# while not the cleanest way, this is where we put our surface planes for now
class CCollidable(Component):
	def __init__(self, planes:list):
		super(CCollidable, self).__init__("Collidable")
		self._planes = planes
	
	@property
	def planes(self):
		return self._planes

class CTransform2(Component):
	def __init__(self, pos:Point2, v_dir:Vec2):
		super(CTransform2, self).__init__(component_type='Transform2')
		self.position = pos
		self._viewing_direction = v_dir

	@property
	def position(self):
		return self._position

	@position.setter
	def position(self, v):
		if not v:
			v = Point2(0, 0)

		if (isinstance(v, tuple)):
			self._position = Point2(v[0], v[1])
		elif (isinstance(v, Point2)):
			self._position = v
		else:
			raise ValueError("v is not of the correct type")			

	@property
	def x(self, v):
		return self._position.x
	
	@property
	def y(self):
		return self._position.y

	@property
	def viewing_direction(self):
		return self._viewing_direction

	@viewing_direction.setter
	def viewing_direction(self, dir:Vec2):
		self._viewing_direction = dir

class UpdatePositionMessage(Message):
	def __init__(self, dpos:Vec2):
		super(UpdatePositionMessage, self).__init__("UpdatePosition")
		self._delta_position = dpos

	@property
	def delta_position(self):
		return self._delta_position

class UpdateOrientationMessage(Message):
	def __init__(self, dangle:float):
		super(UpdateOrientationMessage, self).__init__("UpdateOrientation")
		self._delta_orientation = dangle
	
	@property
	def delta_orientation(self):
		return self._delta_orientation

class CFieldOfView(Component):
	def __init__(self, fov_angle_rad:float = pi / 2., fov_distance:int = 10):
		super(CFieldOfView, self).__init__(component_type="FieldOfView")
		self._fov_alpha = fov_angle_rad
		self._fov_z     = fov_distance

	@property
	def angle(self):
		return self._fov_alpha
	
	@property
	def distance(self):
		return self._fov_z

class CVelocity(Component):
	def __init__(self, velocity:float):
		super(CVelocity, self).__init__(component_type='Velocity')
		self._velocity = velocity

class SInput(System):
	def __init__(self):
		super(SInput, self).__init__()

	@staticmethod
	def arrow_key_pressed(km):
		return km[pygame.K_LEFT] or km[pygame.K_RIGHT] or km[pygame.K_DOWN] or km[pygame.K_UP]

	def update(self, time_delta, entities):
		if len(entities) < 1:
			return None

		key_pressed = pygame.event == pygame.KEYDOWN
		key_up      = pygame.event == pygame.KEYUP
		key_map = pygame.key.get_pressed()		

		if SInput.arrow_key_pressed(key_map):
			dx, dy = 0., 0., 
			dalpha = 0.05			
			position_entities = [e for e in entities if e.has_component_type("Transform2")]

			if key_map[pygame.K_LEFT] or key_map[pygame.K_a]:
				for pe in position_entities:
					pe.send_msg(UpdateOrientationMessage(dangle=-dalpha))

			if key_map[pygame.K_RIGHT] or key_map[pygame.K_d]:
				for pe in position_entities:					
					pe.send_msg(UpdateOrientationMessage(dangle= dalpha))

			# move forward/ backward
			if key_map[pygame.K_UP] or key_map[pygame.K_w]:
				for pe in position_entities:
					d = pe.get_of_type("Transform2").viewing_direction
					pe.send_msg(UpdatePositionMessage(dpos=d))

			if key_map[pygame.K_DOWN] or key_map[pygame.K_s]:
				for pe in position_entities:
					d = pe.get_of_type("Transform2").viewing_direction
					pe.send_msg(UpdatePositionMessage(dpos=-d))

	def send_msg(self, msg):
		return super().send_msg(msg)

	def receive_msg(self, msg):
	 return super().receive_msg(msg)

class SRender(System):
	C_WHITE = (255, 255, 255)
	C_GRAY = (192, 192, 192)
	C_BLUE  = (0, 0, 255)
	C_BLACK = (0, 0, 0)
	C_VDARK_GRAY = (32, 32, 32)
	C_DARK_GRAY  = (92, 92, 92)

	def __init__(self, screen_width, screen_height):
		super(SRender, self).__init__()
		self.screen_width = screen_width
		self.screen_height= screen_height
		
		self.screen_buffer = pygame.display.set_mode(size=(self.screen_width, self.screen_height))
		self.back_buffer = pygame.Surface(self.screen_buffer.get_size())
		self.back_buffer = self.back_buffer.convert()

	def clear_back_buffer(self):
		self.back_buffer.fill(SRender.C_BLACK)		

	def update(self, time_delta, entities):
		if len(entities) < 1:
			return None

		pvis = [e for e in entities if e.has_component_type("Collidable")]
		
		# for now we just render everyone having a position component
		# and do not care about the projection from world space coordinates to camera space
		renderables = [e for e in entities if e.has_component_type("Renderable") and e.has_component_type("Transform2")]

		# clear the backbuffer
		self.clear_back_buffer()

		for e in renderables:
			# get the position of the renderable and draw it - for now we assume that there is only one
			pos = e.get_of_type("Transform2").position
			rx  = e.get_of_type("Renderable")
			col = rx.color
			
			if rx.shape == Shape.Point:
				pygame.draw.circle(self.back_buffer, col, (int(pos.x), int(pos.y)), 5, 0)
			elif rx.shape == Shape.Square:
				pygame.draw.rect(self.back_buffer, SRender.C_DARK_GRAY, (pos.x, pos.y, rx.width, rx.width), 1)
			else:
				pass

		fov_entity = [e for e in entities if e.has_component_type("FieldOfView") and e.has_component_type("Transform2")]

		if fov_entity:
			for e in fov_entity:
				transform = e.get_of_type("Transform2")
				fov = e.get_of_type("FieldOfView")

				pos, dvec = transform.position, transform.viewing_direction
				view_dist = fov.distance				
				dvec_alpha = dvec.to_angle()
				fov_angle = fov.angle				
				falpha1, falpha2 = (dvec_alpha - fov_angle/2.) % (2. * pi), dvec_alpha + fov_angle/2. % (2. * pi)
				N_sample = int(elisa.linalg.rad_to_angle(fov_angle))
				v1 = Vec2.from_angle(falpha1) * view_dist
				v2 = Vec2.from_angle(falpha2) * view_dist
				dv = (v2 - v1 ) / N_sample
				pdvi = v1

				pv1, pv2 = pos + v1, pos + v2
				pygame.draw.polygon(self.back_buffer, SRender.C_VDARK_GRAY, [(pos.x, pos.y), (pv1.x, pv1.y), (pv2.x, pv2.y)], 0)

				for i in range(N_sample):
					# perform the collision test
					ppvi = pos + pdvi					
					pdvi = pdvi + dv
					rayi = Ray2(origin=pos, direction=pdvi)					
					for vis in pvis:
						visplanes = vis.get_of_type("Collidable").planes
						vpos      = vis.get_of_type("Transform2").position
						vrx       = vis.get_of_type("Renderable")

						intersects = False
						for planei in visplanes:
							r, t, _ip = elisa.linalg.intersection2(rayi, planei)
							if r and 0 <= t <= pdvi.length and elisa.linalg.inside_square2(vpos.x, vpos.y, vrx.width, _ip):
								intersects = True								
								break

						if intersects:
							pygame.draw.line(self.back_buffer, SRender.C_GRAY, (pos.x, pos.y), (ppvi.x, ppvi.y), 1)
							pygame.draw.rect(self.back_buffer, SRender.C_WHITE, (vpos.x, vpos.y, vrx.width, vrx.width), 1)

				pygame.draw.circle(self.back_buffer, SRender.C_DARK_GRAY, (int(pos.x), int(pos.y)), int(view_dist), 1)

		self.screen_buffer.blit(self.back_buffer, (0, 0))
		pygame.display.flip()

		return None

def init_ecs(screen_width, screen_height, verbose:bool=True):
	if verbose:
		print("Initializing ECS objects")
	# we put the player at 0,0 at let her view at positive x=+1
	entities, components, systems = [], [], []

	ctrans = CTransform2(pos=Point2(100, 100), v_dir=Vec2(1, 0))
	cvel = CVelocity(velocity=5)
	cfov = CFieldOfView(fov_angle_rad=pi/4., fov_distance=100.)
	crnd = CRenderable(render_color=(64, 64, 228))
	components.append(ctrans)
	components.append(cvel)
	components.append(cfov)
	components.append(crnd)

	e_player = EPlayer().add(ctrans).add(cvel).add(crnd).add(cfov)
	entities.append(e_player)

	box_pos_x = (50, 100, 200, 400, 450, 500, 550, 600, 620)
	box_pos_y = (100, 200, 50, 100, 300, 400, 250, 100, 225)
	box_width = (20,   50, 10,  40,  20,  30,  50,  10,  10)

	# since these are all oriented the same, we can reuse the surface normals here
	normals = [Vec2(0, 1), Vec2(1, 0), Vec2(0, -1), Vec2(-1, 0)]

	for i, p in enumerate(zip(box_pos_x, box_pos_y)):
		ctrans = CTransform2(p, Vec2(0, 0))
		crnd = CRenderable(render_color=(200, 200, 200), shape=Shape.Square, width=box_width[i])		
		components.append(ctrans)
		components.append(crnd)		

		n1 = Vec2(0, 1)
		o1 = Vec2(p[0] + box_width[i] // 2, p[1])
		p1 = Plane2(n1, o1)

		n2 = Vec2(1, 0)
		o2 = Vec2(p[0] + box_width[i], p[1] + box_width[i] // 2)
		p2 = Plane2(n2, o2)

		n3 = Vec2(0, -1)
		o3 = Vec2(p[0] + box_width[i] // 2, p[1] + box_width[i])
		p3 = Plane2(n3, o3)

		n4 = Vec2(-1, 0)
		o4 = Vec2(p[0], p[1] + box_width[i] // 2)
		p4 = Plane2(n4, o4)

		planes = [p1, p2, p3, p4]
		ccol = CCollidable(planes=planes)
		components.append(ccol)
		e_box = EBox().add(ctrans).add(crnd).add(ccol)
		entities.append(e_box)
	
	systems.append(SInput())
	systems.append(SRender(screen_width, screen_height))

	return components, entities, systems

def main():
	if not pygame.font: print("Pygame - fonts not loaded")
	if not pygame.mixer: print("Pygame - audio not loaded")

	pygame.init()

	S_WIDTH, S_HEIGHT, S_TITLE = 640, 480, "Elisa 17 - ray casting"
	
	pygame.display.set_caption(S_TITLE)
	pygame.mouse.set_visible(True)

	# FPS watcher
	fps_watcher = pygame.time.Clock()
	is_done = False

	components, entities, systems = init_ecs(S_WIDTH, S_HEIGHT)

	while not is_done:
		elapsed_millis = fps_watcher.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				is_done = True
				break

		for _sys in systems:
			_sys.update(time_delta=elapsed_millis, entities=entities)

if __name__ == '__main__':
	main()