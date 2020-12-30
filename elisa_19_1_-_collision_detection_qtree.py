# name: elisa_19_1_-_collision_detection_qtree.py
# auth: (c) 2020 christian bitter
# desc: in the previous example, we implemented axis aligned bounding boxes as
# a simple mechanism for checking for collisions between objects.
# However, in scenes with a large number of objects,
# the pair-wise checking of inter-object collisions, becomes cumbersome and slow really soon.
# So, in order to improve this, we also go for a spatial data structure the quad tree
# source for reference:
# Computer Science 420 (University of San Francisco): Game Engineering
# https://www.cs.usfca.edu/~galles/cs420S13/lecture/intersection2D.pdf
# https://www.cs.usfca.edu/~galles/cs420S13/lecture/SpatialDataStructures.pdf

# TODO: documentation

# NOTE: QuadTree rebalancing will be done when moved into Elisa

from __future__ import annotations

import pygame

from elisa.linalg import Poly2, Rect2, inside_rect2, intersects_AABB2


def on_quit():
    print("Elisa -> Quit()")


class QuadTreeNode(object):
    """An indiviudal Node in the QuadTree. This is composed of an area pointer (Rect) denoting the area the node covers,
    and 4 child references to sibling treses.
    """

    def __init__(self, parent: QuadTreeNode, area: Rect2, level: int, max_level: int):
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
        self._max_level = max_level
        self._elements = []

    @property
    def level(self) -> int:
        return self._level

    @property
    def max_level(self) -> int:
        return self._max_level

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

    def insert(self, o) -> int:
        if o is None:
            raise ValueError("o not provided")
        # if o cannot be fit into any subspace insert it into this node directly
        f, r = self.fits_into_subspace(o)
        if f is False or self._level == self._max_level:
            self._elements.append(o)
            return self._level
        else:
            # if required we add a new node
            _t = self._trees[r]
            if _t is None:
                _t = QuadTreeNode(
                    parent=self,
                    area=self._regions[r],
                    level=self._level + 1,
                    max_level=self._max_level,
                )
                self._trees[r] = _t
            return _t.insert(o)

    def update(self, o) -> bool:
        """Updates the QuadTree subtree w.r.t. geometry/ spatial changes occurring to o.
        For example, in the event that o has moved, we might need to allocate it to
        a different region in our node or it has to be moved to a different subtree,
        entirely.

        Args:
            o (any object type that can be stored inside a QuadTree): The object to update

        Raises:
            ValueError: if the object is not provided

        Returns:
            bool: True if the object was updated, else False.
        """
        if o is None:
            raise ValueError("o not provided")

        if o in self._elements:
            # check if o still fits into this node
            #   else remove from here and insert at the parent, so that
            #   updating can be handled there
            if not self._area_rect.inside(o):
                self._elements.remove(o)
                _ = self._parent.insert(o)
                return True
        else:
            _updated = [_t.update(o) for _t in self._trees]

        return any(_updated)

    def replace(self, old, new):
        # this is the same as update, only that we change the
        # object identity from old to new
        if old is None:
            raise ValueError("old not provided")
        if new is None:
            raise ValueError("new not provided")

        _updated = []

        if old in self._elements:
            # check if new still fits into this node - in this case we simply replace the identity
            #   else remove from here and insert at the parent, so that
            #   updating can be handled there
            if not self._area_rect.inside(new):
                self._elements.remove(old)
                u = self._parent.insert(
                    new,
                )
                _updated.append(u)
            else:
                self._elements.remove(old)
                self._elements.append(new)
                _updated.append(True)
        else:
            for _t in self._trees:
                if _t is not None:
                    _updated.append(_t.replace(old, new))

        return any(_updated)

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

    def remove(self, o) -> bool:
        """Remove an object from the Subtree represented by this QuadTree node.

        Args:
            o (any object type that can be stored in a QuadTree node): The object to remove

        Raises:
            ValueError: if the object is not provided an error is raised.

        Returns:
            bool: True if the object was removed, else False
        """
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
        """Checks whether the object o is contained in the region denote by the QuadTree Nodes area.

        Args:
            o (any object supported by Rect2 contained): The object to check

        Returns:
            bool: True if the object is fully contained inside the area, else False.
        """
        if o is None:
            raise ValueError("o not provided")

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
        self._root = QuadTreeNode(parent=None, area=area, level=0, max_level=max_depth)

    @property
    def max_depth(self) -> int:
        return self._max_depth

    @property
    def root(self) -> QuadTreeNode:
        return self._root

    def insert(self, o) -> QuadTree:
        if o is None:
            raise ValueError("o not provided")

        _level = self._root.insert(o)
        self._no_objects += 1

        if _level > self._depth:
            self._depth = _level

        return self

    def query(self, region: Rect2) -> list:
        return self._root.query(region)

    def remove(self, o) -> bool:
        if o is None:
            raise ValueError("o not provided")
        _rem = self.root.remove(o)
        if _rem:
            self._no_objects -= 1
        return _rem

    def update(self, o):
        return self._root.update(o)

    def replace(self, old, new):
        return self._root.replace(old, new)

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

    # we compose a scene of ...
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

    entities.append(poly7)
    q_tree.insert(poly7)

    # for introspection
    print(q_tree)
    print("Removing poly: {}".format(q_tree.remove(poly7)))
    print(q_tree)

    # now we define a query region ... something that we might be interested in
    # when doing our collision detection
    proposal_region = Rect2.from_points(300, 220, 500, 320)

    # we are going to update one poly along the x-axis.
    # this will be based on copying/ creating new objects, which is somewhat wasteful
    # for the purposes of the tutorial and the current code base, this is what we do
    _move_x_min, _move_x_max = 100, 600
    update_poly = poly5
    dir_x = 1.0

    while not is_done:
        _ = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

        back_buffer.fill(c_black)

        # update the two polys - this is wasteful ...
        _pminx, _pminy, _pmaxx, _pmaxy = update_poly.AABB

        if _pminx + (_pmaxx - _pminx) >= _move_x_max or _pminx <= _move_x_min:
            dir_x *= -1.0

        dx = dir_x * 1.0
        new_poly: Poly2 = Poly2.translate(update_poly, dx, 0.0)
        # update entities
        entities.remove(update_poly)
        entities.append(new_poly)

        # update the quad tree
        q_tree.replace(update_poly, new_poly)

        # replace the object identity
        update_poly = new_poly

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

    pygame.quit()


if __name__ == "__main__":
    main()
