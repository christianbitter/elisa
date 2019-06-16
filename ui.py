# name: ui.py
# auth: christian bitter
# desc: building simple ui with pygame
# TODO:
# we need to ensure that rendering is blitting to the callers x, y coordinates
# controls render into their surface in local coordinates
# todo: font vertical alignment
# todo: font horizontal alignment
# todo: ui elements need to be re-rendered upon invaliation
# todo: ui element text box
# todo: ui element label
# todo: support for rendering form with background and alpha blending of controls
# todo: having to forward the pygame event loop events to the controls is cumbersome, there
#   should be something cleaner
# todo: there should be something like overlays - where we have one form and can create smaller one blending it
#   over the existing one.
# todo: add unit testing
# todo: controls should have a global coordinate pair as well, this would simplify the hit-testing

import pygame
from enum import Enum, IntFlag

C_BLACK = (0, 0, 0, 255)
C_RED = (255, 0, 0, 255)
C_GREEN = (0, 255, 0, 255)
C_BLUE = (0, 0, 255, 255)
C_MENUGRAY = (192, 192, 192, 255)
C_FORMBLUE = (32, 32, 128, 255)
C_WHITE = (255, 255, 255, 255)

I_MARGIN = 3


def xy_inside(x: int, y: int, x0: int, y0: int, w: int, h: int) -> bool:
    return x0 <= x <= x0 + w and y0 <= y <= y0 + h

# TODO: GUI - the main gui manager
class GUI():
    """"""

    def __init__(self, ):
        """Constructor for GUI"""
        super(GUI, self).__init__()


class FillStyle(Enum):
    Empty = 1
    Colour = 2
    Image = 3


class VerticalAlignment(Enum):
    Center = 0
    Top = 1
    Bottom = 2


class HorizontalAlignment(Enum):
    Center = 0
    Left = 1
    Right = 2


class FontStyle(IntFlag):
    Normal = 0,
    Bold = 1,
    Italic = 2,
    Underline = 8


class UIElement(object):
    """"""

    def __init__(self, name, x: int = None, y: int = None, w: int = 0, h: int = 0,
                 **kwargs):
        """Constructor for UIElement"""
        super().__init__()
        self._name = name
        self._x0 = x
        self._y0 = y
        self._w = w
        self._h = h
        self._x1 = None
        self._y1 = None
        if self._x0 is not None and self._w is not None:
            self._x1 = x + w
        if self._y0 is not None and self._h is not None:
            self._y1 = y + h
        self._client_rect = (0, 0, self._w, self._h)
        self._invalidated = True

    @property
    def name(self):
        return self._name

    @property
    def x(self):
        return self._x0

    @x.setter
    def x(self, x: int):
        if not x:
            raise ValueError("x")
        if x < 0:
            raise ValueError("x < 0")

        if self._x0 != x:
            self._x0 = x
            self._x1 = self._x0 + self._w
            self.invalidate()

    @property
    def y(self):
        return self._y0

    @y.setter
    def y(self, y: int):
        if not y:
            raise ValueError("y")
        if y < 0:
            raise ValueError("y < 0")

        if self._y0 != y:
            self._y0 = y
            self._y1 = self._y0 + self._h
            self.invalidate()

    @property
    def width(self):
        return self._w

    @width.setter
    def width(self, w:int):
        if not w:
            raise ValueError("w")
        if w < 0:
            raise ValueError("w < 0")

        if self._w != w:
            self._w = w
            self._x1 = self._x0 + w
            self.invalidate()

    @property
    def height(self):
        return self._h

    @height.setter
    def height(self, h: int = None):
        if not h:
            raise ValueError("h")
        if h < 0:
            raise ValueError("h < 0")

        if self._h != h:
            self._h = h
            self._y1 = self._y0 + h
            self.invalidate()

    def invalidate(self):
        self._client_rect = (0, 0, self._w, self._h)
        self._invalidated = True

    def get_bounds(self):
        return self._x0, self._y0, self._x1, self._y1

    def __repr__(self):
        return "UIElement: {} ({})".format(self._name, type(self))


class Renderable(UIElement):
    """"""

    def __init__(self, name, x: int = None, y: int = None, w: int = None, h: int = None, **kwargs):
        """Constructor for Renderable"""
        super().__init__(name, x=x, y=y, w=w, h=h, kwargs=kwargs)

        self._fill_style = kwargs.get('fill_style', FillStyle.Empty)
        self._background_colour = kwargs.get('background_colour', (128, 128, 128, 255))
        self._background_image = kwargs.get('background_image', None)
        self._colour = kwargs.get('colour', (0, 0, 0))
        self._show_border = kwargs.get('show_border', True)
        self._show_caption = kwargs.get('show_caption', False)
        self._caption = kwargs.get("caption", "")
        self._font_size = kwargs.get('font_size', 20)  # width and height is determined by font
        self._font_style = kwargs.get('font_style', FontStyle.Normal)
        self._font = pygame.font.Font(kwargs.get('font', pygame.font.get_default_font()), self._font_size)
        self._font_colour = kwargs.get('font_colour', C_BLACK)

        self._caption_halign = kwargs.get('caption_halign', HorizontalAlignment.Center)
        self._caption_valign = kwargs.get('caption_valign', VerticalAlignment.Center)

        self._apply_font_style()

        self._text_caption = None
        self._text_bounds = None

        if self._show_caption and self._caption is not None:
            self._text_caption = self._font.render(self._caption, 1, self._font_colour)
            self._text_bounds = self._text_caption.get_rect()
            # we add a safety buffer around the text bounds to allow for the real bounds
            w, h = self._text_bounds[2] + 2 * I_MARGIN, self._text_bounds[3] + 2 * I_MARGIN
            if self.width is None or self.width < w:
                self.width = w
            if self.height is None or self.height < h:
                self.height = h

        self._surface = None
        if self.width is not None and self.height is not None:
            self._surface = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)

    def _apply_font_style(self):
        if self._font_style & FontStyle.Bold:
            self._font.set_bold(True)
        if self._font_style & FontStyle.Italic:
            self._font.set_italic(True)
        if self._font_style & FontStyle.Underline:
            self._font.set_underline(True)

    @property
    def background_colour(self):
        return self._background_colour

    @property
    def colour(self):
        return self._colour

    @property
    def show_border(self):
        return self._show_border

    def invalidate(self):
        UIElement.invalidate(self)
        if self._w is not None and self._h is not None:
            self._surface = pygame.Surface((self._w, self._h), flags=pygame.SRCALPHA)

    @property
    def caption(self):
        return self._caption

    @property
    def show_caption(self):
        return self._show_caption

    def _paint(self):
        self._surface.fill(C_BLACK)
        if self._fill_style == FillStyle.Colour:
            pygame.draw.rect(self._surface, self._background_colour, self._client_rect, 0)
        elif self._fill_style == FillStyle.Image:
            if not self._background_image:
                raise ValueError("background fill image but image not provided")

            scaled_bgimg = pygame.transform.scale(self._background_image.image, (self._w, self._h))
            self._surface.blit(scaled_bgimg, dest=self._client_rect)
        else:
            pass

        if self._show_border:
            pygame.draw.rect(self._surface, self._colour, self._client_rect, 1)

        if self._show_caption and self._caption != '':
            # TODO: respect - alignment settings
            self._surface.blit(self._text_caption, dest=(I_MARGIN, I_MARGIN))

        self._invalidated = False

    def render(self, buffer):
        if self._invalidated:
            self._paint()
        buffer.blit(self._surface, (self.x, self.y))


class Clickable(Renderable):
    """"""

    def __init__(self, name, x: int = None, y: int = None, w: int = None, h: int = None, **kwargs):
        """Constructor for Clickable"""
        super().__init__(name, x=x, y=y, w=w, h=h, **kwargs)
        self._is_clicked = False

    def unclick(self):
        self._is_clicked = False

    def clicked(self, mx, my, button):
        previous_state = self._is_clicked
        if xy_inside(mx, my, self._x0, self._y0, self._w, self._h):
            self._is_clicked = True
        else:
            self._is_clicked = False

        if previous_state != self._is_clicked:
            self.invalidate()

        return self._is_clicked, self

    def on_click(self, sender, x, y, button):
        # when clicked this fires, it needs to be overwritten in a derived class
        pass


class Button(Clickable):
    """"""

    def __init__(self, name, x: int, y: int, w: int = None, h: int = None, **kwargs):
        """Constructor for Button"""
        super().__init__(name=name, x=x, y=y, w=w, h=h, **kwargs)

    def _paint(self):
        Clickable._paint(self)

        if self._is_clicked:
            pygame.draw.rect(self._surface, C_RED, self._client_rect, 2)


class MenuItem(Button):
    """"""

    def __init__(self, name: str, caption:str, w: int = None, h: int = None, **kwargs):
        """Constructor for MenuItem"""
        kwargs['caption'] = caption
        kwargs['show_caption'] = True
        kwargs['show_border'] = True
        kwargs['fill_style'] = FillStyle.Colour
        super().__init__(name=name, x=0, y=0, w=w, h=h,
                         **kwargs)


class Menu(Clickable):
    """"""
    MENU_ITEM_INNER_MARGIN = 3

    def __init__(self, name, x, y, **kwargs):
        """Constructor for Menu"""
        # if the user did not override these settings then we add our defaults
        if 'colour' not in kwargs:
            kwargs['colour'] = C_BLACK
        if 'background_colour' not in kwargs:
            kwargs['background_colour'] = C_MENUGRAY
        if 'show_border' not in kwargs:
            kwargs['show_border'] = True
        if 'fill_style' not in kwargs:
            kwargs['fill_style'] = FillStyle.Colour
        super().__init__(name=name, x=x, y=y,
                         w=2 * Menu.MENU_ITEM_INNER_MARGIN,
                         h=2 * Menu.MENU_ITEM_INNER_MARGIN,
                         **kwargs)
        self._items = {}
        self._item_names = []

    def add_item(self, mni: MenuItem):
        """
        Add a menu item to the existing menu items.
        :param m: the menu item to add
        """
        if not mni:
            raise ValueError("Item not provided")

        i_margin = Menu.MENU_ITEM_INNER_MARGIN

        i_x = i_margin
        if len(self._item_names) < 1:  # first item
            if self._show_caption:
                i_y = i_margin + self._text_bounds[3]
            else:
                i_y = i_margin
            self.height = self.height + mni.height
        else:
            last_item = self._items[self._item_names[len(self._item_names) - 1]]
            i_y = last_item.y + last_item.height + i_margin
            self.height = i_y + mni.height + i_margin

        # TODO: there should be a single method to set this, to avoid constant invalidation
        mni.x = i_x
        mni.y = i_y

        if mni.width >= self.width:
            self.width = 2 * i_margin + mni.width
            for _, mi in self._items.items():
                mi.width = mni.width
        else:
            mni.width = self.width - 2 * i_margin

        # now add and invalidate
        self._items[mni.name] = mni
        self._item_names.append(mni.name)
        self.invalidate()

    @property
    def caption(self):
        return self._caption

    @property
    def item_names(self):
        return self._item_names

    @property
    def items(self):
        return self._items

    def __getitem__(self, item):
        if item is None:
            raise ValueError("getitem - key not provided")

        if isinstance(item, int):
            return self._items[self._item_names[item]]
        else:
            if item in self._items:
                return self._items[item]

        raise ValueError("SpriteMap.get - undefined sprite selected")

    def unclick(self):
        Clickable.unclick(self)
        for _, c in self._items.items():
            c.unclick()

    def clicked(self, mx, my, button):
        is_clicked, sender = Clickable.clicked(self, mx, my, button)
        # now ask for each menu item
        # for this we need to translate the mouse coord into the local coords by subtracting the parents offset
        lx, ly = mx - self.x, my - self.y
        for _, c in self._items.items():
            is_clicked_i, sender_i = c.clicked(lx, ly, button)
            if is_clicked_i:
                is_clicked, sender = is_clicked_i, sender_i

        return is_clicked, sender

    def _paint(self):
        Clickable._paint(self)
        for _, m in self._items.items():
            m._paint()

    def render(self, buffer):
        if not self._show_caption and len(self._item_names) < 1:
            return

        if self._invalidated:
            self._paint()

        Clickable.render(self, buffer)

        for _, m in self._items.items():
            m.render(self._surface)

        buffer.blit(self._surface, (self._x0, self._y0))


class GameScreen(Clickable):
    """"""

    def __init__(self, name, title, width, height, **kwargs):
        """Constructor for GameScreen"""
        if 'fill_style' not in kwargs:
            kwargs['fill_style'] = FillStyle.Colour
        if 'background_colour' not in kwargs:
            kwargs['background_colour'] = C_FORMBLUE

        super().__init__(name, x=0, y=0, w=width, h=height, **kwargs)
        self._title = title
        self._components = {}

        self._initialize_components()

    def _initialize_components(self):
        pass

    def screen_transition(self):
        pass

    def paint(self):
        Clickable.paint(self)
        for _, ui_elem in self._components.items():
            if isinstance(ui_elem, Renderable):
                ui_elem.paint()

    def render(self, buffer):
        Clickable.render(self, buffer)

        for _, ui_elem in self._components.items():
            if isinstance(ui_elem, Renderable):
                ui_elem.render(self._surface)

        buffer.blit(self._surface, (self._x0, self._y0))

    def unclick(self):
        Clickable.unclick(self)
        for _, c in self._components.items():
            c.unclick()

    def add_component(self, c):
        if not c:
            raise ValueError("component to add not provided")
        self._components[c.name] = c

    def remove_component(self, c_name: str):
        if not c_name:
            raise ValueError("component name is missing")

        del self._components[c_name]

    def clicked(self, mx, my, button):
        # check for self and all child elements if they are clicked the one with the smallest hitbox wins
        # if no child is clicked, see if we are clicked
        is_clicked, sender = Clickable.clicked(self, mx, my, button)

        for _, c in self._components.items():
            is_clicked_i, sender_i = c.clicked(mx, my, button)
            if is_clicked_i:
                is_clicked, sender = is_clicked_i, sender_i

        return is_clicked, sender