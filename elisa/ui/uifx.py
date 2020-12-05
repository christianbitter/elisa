import pygame

# TODO: alphabet for segment display
# TODO: scrolling text effect

sd_chars = {
    0: [
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ],
    1: [
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
    ],
    2: [
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [1, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 1, 1, 1],
    ],
    3: [
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [1, 1, 1, 1],
    ],
    4: [
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
    ],
    5: [
        [1, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [1, 1, 1, 1],
    ],
    6: [
        [1, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ],
    7: [
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
    ],
    8: [
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ],
    9: [
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [1, 1, 1, 1],
    ],
}

sd_size = {"small": 9, "medium": 11, "large": 15}


def digit_inner_margin(size):
    return {"small": 1, "medium": 2, "large": 3}.get(size, "medium")


def digit_outer_margin(size):
    return digit_inner_margin(size) + 1


def digit_width(size):
    return (
        4 * sd_size[size] + 2 * digit_outer_margin(size) + 3 * digit_inner_margin(size)
    )


def digit_height(size):
    return (
        7 * sd_size[size] + 2 * digit_outer_margin(size) + 6 * digit_inner_margin(size)
    )


# TODO: we render the segment display at x, y
# individual circles with some define spacing in-between and a defined colour


class SegmentDisplay(pygame.sprite.Sprite):
    """
    A simple graphical segment display
    """

    def __init__(
        self, x: int, y: int, value, size, colour=(255, 255, 255, 255), **kwargs
    ):
        """Constructor for SegmentDisplay"""
        pygame.sprite.Sprite.__init__(self)
        self._x = x
        self._y = y
        self._surface_width = digit_width(size)
        self._surface_height = digit_height(size)

        self.image = pygame.Surface((self._surface_width, self._surface_height))
        self.rect = pygame.Rect(x, y, self._surface_width, self._surface_height)

        self._background_colour = kwargs.get("backgound_colour", (0, 0, 0, 255))
        self._value = value
        self._invalid = True
        self._size = size
        self._colour = colour

    @property
    def background_colour(self):
        return self._background_colour

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self._invalid = True

    def invalidate(self):
        self._invalid = True

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def render(self, buffer):
        if self._invalid:
            buffer.fill(self._background_colour)

            c = sd_chars[self._value]
            r = sd_size[self._size]
            mo = digit_outer_margin(self._size)
            mi = digit_inner_margin(self._size)
            r2 = int(r / 2)

            x0, y0 = mo + r2, mo + r2
            _y = y0
            for iy, ry in enumerate(c):
                _x = x0
                for ix, d in enumerate(ry):
                    if d == 1:
                        pygame.draw.circle(
                            buffer, self._colour, (int(_x), int(_y)), r2, 0
                        )
                    pygame.draw.circle(
                        buffer, (64, 64, 64, 255), (int(_x), int(_y)), r2, 1
                    )
                    _x = _x + mi + r
                _y = _y + mi + r
            self._invalid = False

    def update(self, *args):
        if self._invalid:
            self.render(self.image)
            self._invalid = False

    @property
    def surface_width(self):
        return self._surface_width

    @property
    def surface_height(self):
        return self._surface_height


class TwoDigitCounter(pygame.sprite.Sprite):
    """
    A graphical two digit counter, siuch as a timer clock realized via the segment display
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        size: str = "medium",
        initial_value: int = 0,
        dv: int = 1,
        colour=(64, 224, 64, 255),
        decrement: bool = False,
        **kwargs
    ):
        """Constructor for DigitalClock"""
        pygame.sprite.Sprite.__init__(self)
        self._initial_value = initial_value
        self._colour = colour
        self._name = name
        self._size = size
        self._x = x
        self._y = y
        self._background_colour = kwargs.get("backgound_colour", (0, 0, 0, 255))
        self._value = self._initial_value
        v0, v1 = int(initial_value / 10), initial_value % 10
        self._d0 = SegmentDisplay(
            size=self._size,
            x=self._x,
            y=self._y,
            value=v0,
            colour=colour,
            backgound_colour=self._background_colour,
        )
        self._d1 = SegmentDisplay(
            size=self._size,
            x=self._x + self._d0.surface_width,
            y=self._y,
            value=v1,
            colour=colour,
            backgound_colour=self._background_colour,
        )
        self._surface_width = self._d0.surface_width + self._d1.surface_width
        self._surface_height = self._d0.surface_height
        self._change_by = dv
        self.image = pygame.Surface((self._surface_width, self._surface_height))
        self.rect = pygame.Rect(
            self._x, self._y, self._surface_width, self._surface_height
        )
        self._on_limit_reached = None
        if dv > 0 and decrement:
            raise ValueError("Cannot decrement with positive change value")
        if dv < 0 and not decrement:
            raise ValueError("Cannot increment with negative change value")
        self._decrement = decrement
        self._invalid = True
        # update on creation to show something
        self.update()

    @property
    def name(self):
        return self._name

    def reset(self):
        self.value = self._initial_value
        v0, v1 = int(self._initial_value / 10), self._initial_value % 10
        self._d0.value = v0
        self._d1.value = v1
        self._invalid = True

    @property
    def on_limit_reached(self):
        return self._on_limit_reached

    @on_limit_reached.setter
    def on_limit_reached(self, v):
        self._on_limit_reached = v

    @property
    def background_colour(self):
        return self._background_colour

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if not 0 <= v <= 99:
            raise ValueError("value not in 0 ... 59")
        else:
            self._value = v
            v0, v1 = int(self._value / 10), self._value % 10
            self._d0.value = v0
            self._d1.value = v1
            self._invalid = True

    def invalidate(self):
        self._invalid = True

    def tick(self):
        v = max(0, min(99, self._value - 1))
        if (v == 0 or v == 99) and self._on_limit_reached is not None:
            self._on_limit_reached(v)
        self.value = v

    def render(self, buffer):
        i0 = self._d0.image
        i1 = self._d1.image
        buffer.blit(i0, (0, 0))
        buffer.blit(i1, (self._d0.surface_width, 0))

    def draw(self):
        if self._invalid:
            self.render(self.image)
            self._invalid = False

    def update(self, *args):
        if self._invalid:
            self._d0.update(*args)
            self._d1.update(*args)
            self.render(self.image)
            self._invalid = False

    @property
    def surface_width(self):
        return self._surface_width

    @property
    def surface_height(self):
        return self._surface_height
