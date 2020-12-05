# auth: christian bitter
# name:
# desc: here we have a camera following our principal actor, while the actor roams in a simple world.
# the actor is a simple "sprite" - a rect, based on the 4 points. We can move that rect in the principal 4 directions,
# i.e. left, up, down and right. The sprite is implemented as an entity that has a transform component.
# The component has it's local space (0, 0) and extent (w/2, h/2).
# The transform component defines the entities current position in the world.

# We compose a simple world from individual boxes sprinkled in the somewhat close perimeter. This should simulate the notion of
# us actually moving in the environment. Note, we do not implement collision detection here.

# links to content:
# https://www.cs.usfca.edu/~galles/cs420S13/lecture/Transform/Transformation.html
# https://gamedev.stackexchange.com/questions/44256/how-to-add-a-scrolling-camera-to-a-2d-java-game

from pygame.locals import QUIT
import os
from elisa.sprite import SpriteSheet, SpriteAnimation
from elisa.arch.camera import Camera2D
from elisa.linalg import Point3, Vec3, Point2, Vec2
from elisa.linalg.mat3 import translate2D
from elisa.arch.ecs import System, KeyboardInputSystem, Entity, Component, Message
import pygame


def draw_box(s, p1, p2, p3, p4):
    pygame.draw.polygon(s, (192, 128, 228), [p1, p2, p3, p4])
    pygame.draw.polygon(s, (64, 64, 64), [p1, p2, p3, p4], 1)


def draw_player(s, r: int, p0):
    c = (int(p0.x), int(p0.y))
    pygame.draw.circle(s, (192, 128, 228), c, r)
    pygame.draw.circle(s, (64, 64, 64), c, r, 1)


# TODO: once stable this should move into the core
class Transform2DComponent(Component):
    def __init__(self, pos: Point2):
        super(Transform2DComponent, self).__init__("Transform2D")
        self._position = pos
        self._rotation = 0.0
        self._scale = Vec2(1.0, 1.0)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, v: Point2):
        if not v:
            raise ValueError("Position/ Vector not provided")
        self._position = v

    @property
    def transform(self):
        # TODO: return the full transformation matrix
        return translate2D(self._position.x, self._position.y)


class PlayerEntity(Entity):
    def __init__(self, r: int):
        super(PlayerEntity, self).__init__()
        self._radius = r
        self._p0 = Point2(0, 0)

    def _handle_transform_message(self, t_msg: Message):
        c: Transform2DComponent = self.get_of_type("Transform2D")
        td = t_msg.translation
        c.position = c.position + td

    def send_msg(self, msg):
        return {"UpdateTransform2D": self._handle_transform_message(msg)}.get(
            msg.message_type
        )

    @property
    def radius(self):
        return self._radius

    @property
    def points(self):
        return [self._p0]


class BoxEntity(Entity):
    def __init__(self, w, h):
        super(BoxEntity, self).__init__()
        w2 = w // 2
        h2 = h // 2
        self._center = Point2(0, 0)
        self._width = w
        self._height = h
        self._w2 = w2
        self._h2 = h2
        self._p0 = self._center + Vec2(-w2, h2)
        self._p1 = self._center + Vec2(-w2, -h2)
        self._p2 = self._center + Vec2(w2, -h2)
        self._p3 = self._center + Vec2(w2, h2)

    def send_msg(self, msg):
        pass

    @property
    def points(self):
        return [self._p0, self._p1, self._p2, self._p3]


class UpdateTransform2DMessage(Message):
    def __init__(
        self,
        translate_vec: Vec2 = None,
        rotate_alpha: float = None,
        scale_vec: Vec2 = None,
    ):
        super(UpdateTransform2DMessage, self).__init__("UpdateTransform2D")
        self._translate_vec = translate_vec
        self._rotate_alpha = rotate_alpha
        self._scale_vec = scale_vec

    @property
    def rotation_angle(self):
        return self._rotate_alpha

    @property
    def scaleing(self):
        return self._scale_vec

    @property
    def translation(self):
        return self._translate_vec

    def __repr__(self) -> str:
        _str = super(UpdateTransform2DMessage, self).__repr__()
        if self._translate_vec:
            _str += "\r\n\t[+]Translation: {}".format(self._translate_vec)
        return _str

    def __str__(self):
        return self.__repr__()


class RenderSystem(System):
    """The render system is responsible for taking entities from local to screen space"""

    C_BLACK = (0, 0, 0)
    C_WHITE = (250, 250, 250)
    C_BLUE = (0, 0, 255)

    def __init__(self, screen_width: int = 640, screen_height: int = 480):
        super(RenderSystem, self).__init__()
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._screen_buffer = pygame.display.set_mode(
            size=(screen_width, screen_height)
        )
        self._back_buffer = pygame.Surface(self._screen_buffer.get_size())
        self._back_buffer = self._back_buffer.convert()
        self._cam2d = Camera2D(
            ws_xmin=-screen_width,
            ws_xmax=screen_width,
            ws_ymin=-screen_height,
            ws_ymax=screen_height,
            vw_height=screen_height,
            vw_width=screen_width,
        )

    def clear_buffer(self, buffer, clear_color) -> None:
        buffer.fill(clear_color)

    def update(self, time_delta: float, entities: list):
        if not entities or len(entities) < 1:
            return None

        req_update = [e for e in entities if e.has_component_type("Transform2D")]

        self.clear_buffer(self._back_buffer, RenderSystem.C_WHITE)

        # before we update the entities in the world, we need to align the camera with the player.
        # here, we do a simple look for the player and position the camera at some offset from the player
        cam_offset = Vec2(-50, -50)
        player = [e for e in entities if isinstance(e, PlayerEntity)][0]
        # get the current transform - since this will determine our cam position
        p_trans: Transform2DComponent = player.get_of_type("Transform2D")
        p_pos = p_trans.position
        # since we want to align the camera with the players position, we transform him to the origin and apply the
        # camera local-world transformation. we do this by getting the inverse transformation of the player
        # and multiply this with the camera world transformation.
        # since the player is a translation only, we construct the inverse by hand, by taking the negative translation
        inverse_p = translate2D(-p_pos.x, -p_pos.y)
        cam_p = translate2D(cam_offset.x, cam_offset.y)
        final_p = cam_p * inverse_p
        # now here we set the camera world transformation, so that our overall transformation is ...
        # take the primitive, apply the normalized (0,0) to object-local transform
        # take the output and apply the object-local to world transform (final p)
        # we could achieve the same by multiplying final p with the transformation matrix stored in the entity's
        # transform component and applying that
        self._cam2d.mat_ws = final_p

        for e in req_update:
            # the transform component needs to be applied to the entity
            e_trans = e.get_of_type("Transform2D")
            # e_mat   = final_p * e_trans.transform
            e_mat = e_trans.transform
            e_points = e.points

            eg_points = [e_mat * Vec3(p.x, p.y, 1.0) for p in e_points]
            ws_points = [self._cam2d.project_ws(p) for p in eg_points]
            nc_points = [self._cam2d.project_nc(p) for p in ws_points]

            fully_visible = all([self._cam2d.is_visible(p) for p in nc_points])
            if not fully_visible:
                # print("{} is not fully visible".format(e))
                next

            vp_points = [self._cam2d.project_vp(p) for p in nc_points]

            if isinstance(e, PlayerEntity):
                draw_player(self._back_buffer, e.radius, *vp_points)
            else:
                draw_box(self._back_buffer, *vp_points)

        self._screen_buffer.blit(self._back_buffer, (0, 0))
        pygame.display.flip()


# for now we do a simple movement
def handle_key_pressed_event(kb_system):
    def handle_key_pressed(key_map, elapsed_time, entities):
        mov_speed_player_vert = 2.0
        mov_speed_player_horz = 2.0
        if key_map[pygame.K_UP]:
            for e in entities:
                e.send_msg(
                    UpdateTransform2DMessage(
                        translate_vec=Vec2(0.0, -mov_speed_player_horz)
                    )
                )

        if key_map[pygame.K_DOWN]:
            for e in entities:
                e.send_msg(
                    UpdateTransform2DMessage(
                        translate_vec=Vec2(0.0, mov_speed_player_horz)
                    )
                )

        if key_map[pygame.K_LEFT]:
            for e in entities:
                e.send_msg(
                    UpdateTransform2DMessage(
                        translate_vec=Vec2(-mov_speed_player_vert, 0.0)
                    )
                )

        if key_map[pygame.K_RIGHT]:
            for e in entities:
                e.send_msg(
                    UpdateTransform2DMessage(
                        translate_vec=Vec2(mov_speed_player_vert, 0.0)
                    )
                )

    return handle_key_pressed


def setup_ecs() -> tuple:
    trans = Transform2DComponent(Point2(a=0, b=0))
    player = PlayerEntity(r=20).add(trans)
    kb_sys = KeyboardInputSystem()
    t_sys = RenderSystem(screen_width=640, screen_height=480)

    entities = [player]
    components = [trans]
    # we add some very large boxes that are out of view initially, but gradually become visible if we move to the left or right
    # end of the world
    box_pos_x = (-300, -200, -50, 0, 100, 300, 250, 500, 1000, -1000)
    box_pos_y = (-300, 100, -200, 300, -300, 40, 40, 100, 200, 300)
    box_width = (10, 20, 50, 10, 30, 10, 40, 10, 20, 100, 100)

    debug = False
    if debug:
        box_pos_x = ()
        box_pos_y = ()
        box_width = ()

    for (x, y, w) in zip(box_pos_x, box_pos_y, box_width):
        t = Transform2DComponent(pos=Vec2(x, y))
        b = BoxEntity(w=w, h=w).add(t)
        entities.append(b)
        components.append(t)

    kb_sys.on_key_pressed = handle_key_pressed_event(kb_sys)
    systems = {"KEYBOARD": kb_sys, "TRANSFORM": t_sys}
    return entities, components, systems


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    # init pygame - create the main window, and a background surface
    pygame.init()
    S_TITLE = "Elisa 18 - An actor following camera"

    # to start with, we align the virtual world with the physical screen
    entities, components, systems = setup_ecs()

    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    # FPS watcher
    fps_watcher = pygame.time.Clock()
    is_done = False

    # these are world coordinates, so after transformation to the screen the rect should be visible at the same coordinates
    while not is_done:
        _elapsed_ms = fps_watcher.tick(50)

        for event in pygame.event.get():
            if event.type == QUIT:
                is_done = True
                break

        # for now we ignore the render system, but do the rendering on the transformed entity
        for _sys_name in systems:
            systems[_sys_name].update(time_delta=_elapsed_ms, entities=entities)


if __name__ == "__main__":
    main()
