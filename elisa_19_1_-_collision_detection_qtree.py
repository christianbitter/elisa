# name: elisa_19_1_-_collision_detection_qtree.py
# auth: (c) 2020 christian bitter
# desc: implement a simple collision detection mechanism for axis aligned bounding boxes.
# in order to improve this, we also go for a spatial data structure the quadtree
# source for reference:
# Computer Science 420 (University of San Francisco): Game Engineering
# https://www.cs.usfca.edu/~galles/cs420S13/lecture/intersection2D.pdf
# TODO: dynamic scene
# TODO: QuadTree updating
# TODO: QuadTree rebalancing

from __future__ import annotations

import pygame

from elisa.linalg import Poly2, Rect2, inside_rect2, intersects_AABB2


def on_quit():
    print("Elisa -> Quit()")


class QuadTreeNode(object):
    """An indiviudal Node in the QuadTree. This is composed of an area pointer (Rect) denoting the area the node covers,
    and 4 child references to sibling treses.
    """

    def __init__(self, parent: QuadTreeNode, area: Rect2, level: int):
        super(QuadTreeNode, self).__init__()
        self._parent = parent
        self._area_rect = area

        # create the individual hemispheres by subdivision
        x, y, w, h = area.as_p_wh()
        w2, h2 = w // 2, h // 2
        rne: Rect2 = Rect2.from_points(x_min=x + w2, y_min=y, x_max=x + w, y_max=y + h2)
        rse: Rect2 = Rect2.from_points(
            x_min=x + w2, y_min=y + h2, x_max=x + w, y_max=y + h
        )
        rsw: Rect2 = Rect2.from_points(x_min=x, y_min=y + h2, x_max=x + w2, y_max=y + h)
        rnw: Rect2 = Rect2.from_points(x_min=x, y_min=y, x_max=x + w2, y_max=y + h2)

        self._trees = [None, None, None, None]
        self._regions = [rne, rse, rsw, rnw]
        self._level = level
        self._elements = []

    @property
    def level(self) -> int:
        return self._level

    @property
    def elements(self):
        return self._elements

    @property
    def parent(self) -> QuadTreeNode:
        return self._parent

    @property
    def north_east(self) -> QuadTreeNode:
        return self._trees[0]

    @property
    def south_east(self) -> QuadTreeNode:
        return self._trees[1]

    @property
    def south_west(self) -> QuadTreeNode:
        return self._trees[2]

    @property
    def north_west(self) -> QuadTreeNode:
        return self._trees[3]

    def fits_into_subspace(self, o) -> tuple:
        if o is None:
            raise ValueError("o not provided")

        region_fit = [r.inside(o) for r in self._regions]
        for i, rf in enumerate(region_fit):
            if rf:
                return True, i

        return False, -1

    def insert(self, o, max_level: int) -> int:
        if o is None:
            raise ValueError("o not provided")
        # if o cannot be fit into any subspace insert it into this node directly
        f, r = self.fits_into_subspace(o)
        if f is False or self._level == max_level:
            self._elements.append(o)
            return self._level
        else:
            # if required we add a new node
            _t = self._trees[r]
            if _t is None:
                _t = QuadTreeNode(
                    parent=self, area=self._regions[r], level=self._level + 1
                )
                self._trees[r] = _t
            return _t.insert(o, max_level=max_level)

    def __repr__(self) -> str:
        return "4TNode: {}".format(self._area_rect)

    def __str__(self) -> str:
        return self.__repr__()

    def __iter__(self):
        yield self._area_rect

        for t in self._trees:
            if t is not None:
                for st in t.__iter__():
                    yield st

    def remove(self, o):
        if o is None:
            raise ValueError("o not provided")
        if o in self._elements:
            self._elements.remove(o)
            return True
        else:
            for t in self._trees:
                if t is not None and t.remove(o):
                    return True
        return False

    def query(self, region: Rect2) -> list:
        if region is None:
            raise ValueError("region not provided")
        # if the proposal region is contained in this node, return all elements stored in this node
        # additionally ask for any intersection at the child nodes
        # TODO: this is ugly, we might want to add a tuple constructor
        out_nodes = [
            e
            for e in self._elements
            if intersects_AABB2(Rect2.from_points(*list(e.AABB)), region)
        ]

        for t in self._trees:
            if t is not None:
                if intersects_AABB2(a=t._area_rect, b=region):
                    _po = t.query(region)
                    if _po and len(_po) > 0:
                        out_nodes.extend(_po)

        return out_nodes

    def contains(self, o) -> bool:
        if o in self._elements:
            return True

        _contains = [t.contains(o) for t in self._trees if t is not None]

        return any(_contains)


class QuadTree(object):
    def __init__(self, area: Rect2, max_depth: int):
        super(QuadTree, self).__init__()
        self._max_depth = max_depth
        self._depth = 0
        self._no_objects = 0
        self._root = QuadTreeNode(parent=None, area=area, level=0)

    @property
    def max_depth(self) -> int:
        return self._max_depth

    @property
    def root(self) -> QuadTreeNode:
        return self._root

    def insert(self, o) -> QuadTree:
        if o is None:
            raise ValueError("o not provided")

        _level = self._root.insert(o, self._max_depth)
        self._no_objects += 1

        if _level > self._depth:
            self._depth = _level

        return self

    # TODO: query for the objects contained in the proposal region
    def query(self, region: Rect2) -> list:
        return self._root.query(region)

    def remove(self, o) -> bool:
        if o is None:
            raise ValueError("o not provided")
        _rem = self.root.remove(o)
        if _rem:
            self._no_objects -= 1
        return _rem

    def update(self):
        pass

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def no_objects(self) -> int:
        return self._no_objects

    def __repr__(self) -> str:
        return "4Tree(max_depth={}): {} with depth {} and {} objects".format(
            self._max_depth, self._root._area_rect, self._depth, self._no_objects
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __iter__(self):
        return self._root.__iter__()

    def contains(self, o):
        if o is None:
            raise ValueError("o not provided")
        return self._root.contains(o)


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

    pygame.register_quit(on_quit)

    w, h, t = 640, 480, "Elisa - 19.1 Collision Detection - QuadTree"
    c_white = (255, 255, 255)
    c_black = (0, 0, 0)
    c_blue = (0, 0, 255)
    c_light_blue = (64, 64, 255)
    c_red = (255, 0, 0)

    screen_buffer = pygame.display.set_mode(size=(w, h), flags=0)
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill(c_white)

    # here we setup a pygamer clock - we will discuss this in a later example
    fps_watcher = pygame.time.Clock()
    is_done = False

    # we compose a scene of ... two static elements and a moving entity
    # all entities are simple rects

    # r0 = Rect2.from_points(300, 50, 400, 100)
    # r1 = Rect2.from_points(300, 200, 350, 250)
    # r2 = Rect2.from_points(50, 300, 400, 350)
    poly1 = Poly2(points=[(50, 150), (150, 125), (200, 100), (150, 200), (100, 175)])
    poly2 = Poly2(points=[(350, 100), (500, 150), (400, 200), (250, 150)])
    poly3 = Poly2(points=[(400, 300), (500, 300), (450, 325)])
    poly4 = Poly2(points=[(600, 400), (630, 400), (600, 420)])
    poly5 = Poly2(points=[(350, 250), (400, 250), (370, 300)])
    poly6 = Poly2(points=[(350, 20), (400, 50), (370, 100)])
    poly7 = Poly2(points=[(10, 10), (50, 10), (30, 30)])

    entities = [poly1, poly2, poly3, poly4, poly5, poly6]

    # in this we assume that the oob is already computed, i.e. we define it here:
    poly1_oob = [(50, 150), (100, 50), (200, 100), (150, 200)]
    poly2_oob = [(350, 100), (500, 150), (400, 200), (250, 150)]

    world_bounds = Rect2.from_points(0, 0, w, h)

    q_tree = QuadTree(area=world_bounds, max_depth=2)

    for p in entities:
        q_tree.insert(p)

    # print(q_tree)
    # print(q_tree.contains(poly3))
    # print(q_tree.contains(poly7))

    entities.append(poly7)
    q_tree.insert(poly7)
    print(q_tree)
    print("Removing poly: {}".format(q_tree.remove(poly7)))
    print(q_tree)

    proposal_region = Rect2.from_points(300, 220, 500, 320)

    while not is_done:
        _ = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

        back_buffer.fill(c_black)

        for r in q_tree:
            _r: Rect2 = r.points
            pygame.draw.polygon(back_buffer, c_white, _r, 1)

        pygame.draw.polygon(back_buffer, c_red, poly1_oob, 0)
        pygame.draw.polygon(back_buffer, c_red, poly2_oob, 0)

        for r in entities:
            pygame.draw.polygon(back_buffer, c_white, r.points, 1)

        pygame.draw.rect(back_buffer, c_blue, proposal_region.as_p_wh(), 1)

        proposals = q_tree.query(proposal_region)

        for p in proposals:
            pygame.draw.polygon(back_buffer, c_light_blue, p.points, 0)
            pygame.draw.polygon(back_buffer, c_blue, p.points, 1)

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()

    # after exiting the loop we call it Quit - this will invoke our Quit handler and we are free to perform any heavy clean up lifting
    # such as freeing memory or releasing any other resources
    pygame.quit()


if __name__ == "__main__":
    main()
