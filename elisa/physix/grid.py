# Write broadphase.py: a uniform grid keyed on cell coordinates
# with insert, query_aabb and pairs(), plus a brute_force_pairs() of the same interface.
from .body import Body


class UniformGrid:

    def __init__(self, no_cells_x: int, no_cells_y: int):
        self._cells_x = no_cells_x
        self._cells_y = no_cells_y

        self._cells = [([None] * no_cells_x) for i in range(no_cells_y)]

    @property
    def grid(self) -> list:
        return self._cells

    def at(self, x, y):
        return self._cells[y][x]

    def insert(self, o: Body):
        # determine the right cell to insert
        dx = int(o.position.x / self._cells_x)
        dy = int(o.position.y / self._cells_y)

        self.insert_in_cell(dx, dy, o)

    def insert_in_cell(self, x: int, y: int, o):
        if x < 0 or x >= self._cells_x:
            raise ValueError("0 < x < no_cells_x")

        if y < 0 or y >= self._cells_y:
            raise ValueError("0 < y < no_cells_y")

        if not self._cells[y][x]:
            self._cells[y][x] = []

        self._cells_y[y][x].append(o)

    def query_aabb(self):
        raise ValueError("Not implemented")

    def pairs(self):
        raise ValueError("Not implemented")
