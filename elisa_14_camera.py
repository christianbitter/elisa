# auth: christian bitter
# name: elisa_14_camera
# desc: some camera in 2D
# we construct a scene comprised of 3 rects (red, blue, white). the blue rect moves up and down.
# we have two cameras. One camera moves across the scene (which is the same as moving the objects away from the cam).
# this camera moves left and right within some boundary. we see scene objects leaving and entering the visible portion
# of the screen. the other camera aims at simulating a secondary view ... staying fixed on some moving object.
# vers: 0.5

import pygame


class Primitive:
    def __init__(self):
        self._points = []

    @property
    def no_points(self):
        return len(self._points)

    def __len__(self):
        return len(self._points)

    def __iter__(self):
        return iter(self._points)


class Point2(Primitive):
    def __init__(self, x, y):
        super(Point2, self).__init__()
        self._x = x
        self._y = y
        self._points.append((x, y))

    @staticmethod
    def from_tuple(t:tuple):
        if len(t) != 2:
            raise ValueError("Not a 2d tuple")
        return Point2(t[0], t[1])

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __getitem__(self, i):
        if i == 0:
            return self._x
        elif i == 1:
            return self._y
        else:
            raise ValueError("Index out of bounds")

    def __str__(self):
        return "[Point]=({}, {})".format(self._x, self._y)


class Rect2(Primitive):
    def __init__(self, lb: Point2, rt: Point2):
        super(Rect2, self).__init__()

        self._left = lb.x
        self._bottom = lb.y
        self._w = rt.x - lb.x
        self._h = rt.y - lb.y
        self._w2 = self._w * .5
        self._h2 = self._h * .5

        self._center_x = self._left + self._w2
        self._center_y = self._bottom + self._h2

        self._points.append(lb)
        self._points.append(rt)
        self._rect = pygame.rect.Rect(self._left, self._bottom, self._w, self._h)

    @property
    def width(self):
        return self._w

    @property
    def height(self):
        return self._h

    @property
    def centerx(self):
        return self._center_x

    @property
    def centery(self):
        return self._center_y

    @centerx.setter
    def centerx(self, v):
        self._center_x = v
        self._left = self._center_x - self._w2
        self._rect.left = self._left
        lb = Point2(self._left, self._bottom)
        rt = Point2(self._center_x + self._w2, self._bottom)
        self._points = [lb, rt]

    @centery.setter
    def centery(self, v):
        self._center_y = v
        self._bottom = self._center_y - self._h2
        self._rect.bottom = self._bottom
        lb = Point2(self._left, self._bottom)
        rt = Point2(self._left + self._w, self._center_y + self._h2)
        self._points = [lb, rt]

    def __str__(self):
        return "[Rect2]: (cx={}, cy={}, w={}, h={})".format(self._center_x, self._center_y, self._w, self._h)


class Camera:
    """
    Abstract camera
    """
    def __init__(self):
        pass

    def is_visible(self, primitive):
        raise ValueError("Not implemented")

    def project(self, c):
        raise ValueError("Not implemented")


# we take a primitive from world space (we ignore object space for now)
# into the clip space
# normalize it to be in normalized clip space (-1, -1, 1, 1)
    # everything that is outside of this normalized space is clipped or removed
# and transform it to screen/ device space (0, 0, w, h)

class Camera2D(Camera):
    def __init__(self,
                 world_space,
                 cam_space,
                 screen_space=(0, 0, 640, 480),
                 inverted_screen_space=True):
        super(Camera2D, self).__init__()

        self._world_space = world_space
        self._cam_space = cam_space
        self._cam_left = self._cam_space[0]
        self._cam_bottom = self._cam_space[1]
        self._cam_right = self._cam_space[2]
        self._cam_top = self._cam_space[3]
        self._cam_range_x = self._cam_space[2] - self._cam_space[0]
        self._cam_range_xinv = 1. / self._cam_range_x
        self._cam_range_y = self._cam_space[3] - self._cam_space[1]
        self._cam_range_yinv = 1. / self._cam_range_y

        self._cam_x = self._cam_range_x / 2.
        self._cam_y = self._cam_range_y / 2.

        self._hclip_space = [-1, -1, 1, 1]
        self._hclip_left = self._hclip_space[0]
        self._hclip_bottom = self._hclip_space[1]
        self._hclip_right = self._hclip_space[2]
        self._hclip_top = self._hclip_space[3]

        self._hclip_range_x = self._hclip_right - self._hclip_left
        self._hclip_range_y = self._hclip_top - self._hclip_bottom
        self._hclip_range_xinv = 1.0 / self._hclip_range_x
        self._hclip_range_yinv = 1.0 / self._hclip_range_y

        self._screen_space = screen_space
        self._screen_left = self._screen_space[0]
        self._screen_bottom = self._screen_space[1]
        self._screen_right = self._screen_space[2]
        self._screen_top = self._screen_space[3]
        self._screen_range_x = self._screen_right - self._screen_left
        self._screen_range_y = self._screen_top - self._screen_bottom
        self._inverted_screen_space = inverted_screen_space

    def __cam_to_hclip_space__(self, c):
        xc, yc = c[0], c[1]
        _x = self._hclip_left + self._hclip_range_x * self._cam_range_xinv * (xc - self._cam_left)
        _y = self._hclip_bottom + self._hclip_range_y * self._cam_range_yinv * (yc - self._cam_bottom)
        # print("__cam_to_hclip_space__: ({}) => ({})".format((xc, yc), (_x, _y)))
        return _x, _y

    def __hclip_to_screen_space__(self, c):
        xc, yc = c[0], c[1]
        _x = self._screen_left + self._screen_range_x * self._hclip_range_xinv * (xc - self._hclip_left)
        _y = self._screen_bottom + self._screen_range_y * self._hclip_range_yinv * (yc - self._hclip_bottom)
        # print("__hclip_to_screen_space__: ({}) => ({})".format((xc, yc), (_x, _y)))
        return _x, _y

    def __clip__(self, c):
        # TODO: clip
        # xc, yc = c[0], c[1]
        # if not (self._hclip_left <= xc <= self._hclip_right) and (self._hclip_bottom <= yc <= self._hclip_top):
        #     # print("Clipped: ", c)
        #     return True, c
        # else:
        return False, c

    @property
    def is_inverted_screen_y(self):
        return self._inverted_screen_space

    @property
    def cam_x(self):
        return self._cam_x

    @cam_x.setter
    def cam_x(self, v):
        self._cam_x = v
        r2 = .5 * self._cam_range_x
        self._cam_left = v - r2
        self._cam_right = v + r2

    @property
    def cam_y(self):
        return self._cam_y

    def is_visible(self, primitive):
        visibility = []
        for _p in primitive:
            p_vis = self._cam_left <= _p.x <= self._cam_right and self._cam_bottom <= _p.y <= self._cam_top
            visibility.append(p_vis)
        # partial visibility included
        return any(visibility)

    def project(self, primitive: Primitive):
        # transform the primitive
        t_p = []
        for _p in primitive:
            _p = self.__cam_to_hclip_space__(_p)
            t_p.append(_p)

        # now clip
        clipped, clipped_p = self.__clip__(t_p)
        # last projection

        s_p = []
        for _p in clipped_p:
            _p = self.__hclip_to_screen_space__(_p)
            s_p.append(_p)
        if len(s_p) == 1:
            return s_p[0]
        else:
            return s_p

    def __str__(self):
        return "Cam({},{}): {}".format(self._cam_x, self._cam_y, self._cam_space)

def rect_coord2pygame(b, c, w, r0, r1):
    if r0 is None or r1 is None:
        return
    _w = r1[0] - r0[0]
    _h = r1[1] - r0[1]
    pygame.draw.rect(b, c, (r0[0], r0[1], _w, _h), w)


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    pygame.init()

    w, h, t = 640, 480, "Elisa 14 - A 2D camera example"
    c_white = (255, 255, 255)
    c_red   = (255, 0, 0)
    c_blue  = (0, 0, 255)
    c_black = (0, 0, 0)

    virtual_camera = Camera2D(world_space=(-5, 0, 20, 10),
                              cam_space=(0, 0, 10, 10),
                              screen_space=(0, 0, 320, 240))

    follower_camera = Camera2D(world_space=(-5, 0, 20, 10),
                               cam_space=(2, 2, 8, 8),
                               screen_space=(320, 240, 640, 480))

    # now test with a point which should be inside the screen space - should be in the center ...
    p0 = Point2(5, 5)
    _p0 = virtual_camera.project(p0)
    # now test with a point which should be outside the screen space
    p1 = Point2(20, 10)
    _p1 = virtual_camera.project(p1)
    print("{}>P: {} => {}".format(virtual_camera, p0, _p0))  # expect 320, 240
    print("{}>P: {} => {}".format(virtual_camera, p1, _p1))  # None - after clipping

    # now define three rects to show something, the last one is outside the camera when starting
    r0 = Rect2(Point2(2, 0), Point2(10, 10))
    r1 = Rect2(Point2(5, 5), Point2(6, 6))
    r2 = Rect2(Point2(15, 5), Point2(20, 10))

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(c_white)

    fps_watcher = pygame.time.Clock()
    is_done = False

    dir_x = .1
    dir_by = .1

    while not is_done:
        elapsed_millis = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

        back_buffer.fill(c_black)
        if virtual_camera.is_visible(r0):
            p0 = virtual_camera.project(r0)
            rect_coord2pygame(back_buffer, c_red, 0, p0[0], p0[1])
        if virtual_camera.is_visible(r1):
            p1 = virtual_camera.project(r1)
            rect_coord2pygame(back_buffer, c_blue, 0, p1[0], p1[1])
        if virtual_camera.is_visible(r2):
            p2 = virtual_camera.project(r2)
            rect_coord2pygame(back_buffer, c_white, 0, p2[0], p2[1])

        if follower_camera.is_visible(r0):
            p0 = follower_camera.project(r0)
            rect_coord2pygame(back_buffer, c_red, 0, p0[0], p0[1])
        if follower_camera.is_visible(r1):
            p1 = follower_camera.project(r1)
            rect_coord2pygame(back_buffer, c_blue, 0, p1[0], p1[1])
        if follower_camera.is_visible(r2):
            p2 = follower_camera.project(r2)
            rect_coord2pygame(back_buffer, c_white, 0, p2[0], p2[1])

        # while our blue screen moves somewhat nicely, the red rect pops in and out, because
        # it is so large and once one coordinate is outside the clipping space, it simply not be drawn
        # however, we can fix this by implementing a real clipping routine.
        virtual_camera.cam_x = virtual_camera.cam_x + dir_x

        # update the blue rect to move up and down
        r1.centery = r1.centery + dir_by

        if r1.centery >= 8. or r1.centery <= 1:
            dir_by *= -1
        if virtual_camera.cam_x >= 20 or virtual_camera.cam_x <= -5:  # outside of world space
            dir_x *= -1

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    main()
