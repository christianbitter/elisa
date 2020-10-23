# name: elisa_0_1_drawing_shapes.py
# auth: (c) 2020 christian bitter
# desc: Some simple pygame shape drawing and the first use of some linear algebra functions

import pygame as pg
from math import sin, cos, pi
from elisa import Vec2, Point2

C_BLACK = (0, 0, 0)

def draw(buffer):
	"""draw a typical trigonemtric picture, a circle inscribed in a square. and a triangle inscribed into the circle.

	Args:
			buffer ([type]): [description]
	"""
	buffer.fill(C_BLACK)
	lx, ly, w, h = 150, 150, 300, 300
	cx, cy, r = lx + w // 2, ly + h // 2, w // 2
	# now we place one point on the 45° line and another one straight at y = 0
	# note: the orientation of the coordinate system is x-axis down - quadrant 4 is here number 1
	alpha_rad = pi / 4.
	alpha2_rad = alpha_rad / 2.

	t1x, t1y  = cx + r * cos(0), cy + r * sin(0)
	t2x, t2y  = cx + r * cos(alpha2_rad), cy + r * sin(alpha2_rad)
	t3x, t3y  = cx + r * cos(alpha_rad), cy + r * sin(alpha_rad)

	pg.draw.rect(buffer, (128, 128, 255), (lx, ly, w, h), 1)
	pg.draw.circle(buffer, (128, 255, 128), (cx, cy), r, 1)

	p0 = Point2(cx, cy)
	v0 = Vec2(cos(0.), sin(0.)) * r
	v1 = Vec2(cos(alpha2_rad), sin(alpha2_rad)) * r

	# project v1 onto v0 - so that we see subdivision of the larger triangle
	vhat = v0.project_onto(v1) + p0

	pg.draw.polygon(buffer, (92, 64, 64), [(cx, cy), (t1x, t1y), (t2x, t2y)], 1)
	pg.draw.polygon(buffer, (255, 128, 128), [(cx, cy), (t2x, t2y), (t3x, t3y)], 1)
	pg.draw.polygon(buffer, (255, 228, 255), [(cx, cy), (t1x, t1y), (vhat.x, vhat.y), (t3x, t3y)], 1)

def main():
	np, nf = pg.init()
	print(f"Initialization: Pass = {np}, Fail = {nf}")

	w, h, t = 640, 480, "Elisa - 0.1 Drawing Shapes"

	screen_buffer = pg.display.set_mode(size=(w, h))
	pg.display.set_caption(t)
	pg.mouse.set_visible(True)

	back_buffer: pg.Surface = pg.Surface(screen_buffer.get_size())
	back_buffer = back_buffer.convert()

	fps_watcher = pg.time.Clock()
	is_done = False

	while not is_done:
		elapsed_millis = fps_watcher.tick(60)

		for event in pg.event.get():
			if event.type == pg.QUIT:
				is_done = True
				break

		draw(back_buffer)

		if not is_done:
			screen_buffer.blit(back_buffer, (0, 0))
			pg.display.flip()

	pg.quit()

if __name__ == '__main__':
	main()
