from .ray2 import Ray2
from .plane2 import Plane2
from .vec2 import Vec2, Point2

def intersection2(ray:Ray2, plane:Plane2):
	"""Performs the intersection of a 2D ray with a 2D plane. If there is an intersection, the function returns a tuple indicating success
	the parameter t for which the intersection happened and the point of intersection.
	If the ray is perpendicular to the plane, then the result is False and None, None. If the ray points away from the plane, the result
	is False and the negative paramter t is provided, giving None for the point of intersection.

	Args:
			ray (Ray2): Ray to intersect with the plane
			plane (Plane2): Plane to intersect with the ray

	Returns:
			[Triple]: Logical indicating if ray intersects plane, the paramter value for which the intersection happens (if any) and the point
			on the plane where the intersection happens (if any).
	"""
	# if the ray and plane normal are orthogonal no intersection
	d_n_rd = Vec2.dot(plane.normal, ray.direction)
	if d_n_rd == 0.:
		return False, None, None
	# if the ray points into the opposite direction, no intersection with the plane but still a solution
	d_n_rp = Vec2.dot(plane.normal, ray.origin)
	t = (plane.w - d_n_rp) / d_n_rd
	intersects = True if t >= 0 else False
	pos        = None
	if intersects:
		pos = ray.origin + ray.direction * t
	return intersects, t, pos

def inside_rect2(rleftx:float, rlefty:float, w:float, h:float, p:Point2) -> bool:
	"""Check if the point p is contained within the rect defined by left upper point (rleftx, rlefty) and
	tracing out the edges with width and height

	Args:
			rleftx (float): x coordinate of left upper rectangle point
			rlefty (float): y coordinate of left upper rectangle point
			w (float): width of rect
			h (float): height of rect
			p (Point2): point to check for containment

	Returns:
			bool: True if the point is contained inside of the rect
	"""
	px = p.x
	py = p.y

	if (rleftx <= px <= rleftx + w) and (rlefty <= py <= rlefty + h):
		return True
	else:
		return False

def inside_square2(rleftx:float, rlefty:float, w:float, p:Point2) -> bool:
	return inside_rect2(rleftx, rlefty, w, w, p)

def inside_circle2(rleftx:float, rlefty:float, r:float, p:Point2) -> bool:
	raise ValueError("Todo")