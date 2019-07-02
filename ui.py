# name: ui.py
# auth: christian bitter
# desc: building simple ui with pygame
# TODO:
# we need to ensure that rendering is blitting to the callers x, y coordinates
# Controls render into their surface in local coordinates. For that, they have a local rendering surface.
# Control captions/ text can be aligned horizontally and vertically.
# UI elements are re-rendered upon invalidation. In that case the elements paint method is called, causing the
# UI elements surface buffer to be refreshed, so that it can be blitted with valid content subsequently.
# todo: ui element text box
# todo: ui element label
# todo: support for rendering form with background and alpha blending of controls
# todo: having to forward the pygame event loop events to the controls is cumbersome, there
#   should be something cleaner
# todo: there should be something like overlays - where we have one form and can create smaller one blending it
#   over the existing one.
# todo: add unit testing
# todo: controls should have a global coordinate pair as well, this would simplify the hit-testing
# todo: screen transitions either in the screen or in the UI

import pygame
from enum import Enum, IntFlag

C_BLACK = (0, 0, 0, 255)
C_RED = (255, 0, 0, 255)
C_GREEN = (0, 255, 0, 255)
C_BLUE = (0, 0, 255, 255)
C_MENUGRAY = (192, 192, 192, 255)
C_FORMBLUE = (32, 32, 128, 255)
C_ELEMENT_BORDER_DARKGRAY = (64, 64, 64, 255)
C_WHITE = (255, 255, 255, 255)

I_MARGIN = 3


class UIEvent:
    SCREEN_TRANSITION:int = 99999

    @staticmethod
    def transition_screen(event_from:str, event_to:str):
        return pygame.event.Event(pygame.USEREVENT,
                                  {
                                      "mode": UIEvent.SCREEN_TRANSITION,
                                      "source" : event_from,
                                      "target" : event_to
                                  })

def xy_inside(x: int, y: int, x0: int, y0: int, w: int, h: int) -> bool:
    return x0 <= x <= x0 + w and y0 <= y <= y0 + h

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
    """
    This is the base type of all UI elements. Critically, it has a name/id and some
    spatial location and extent.
    """

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
        self._has_focus = False

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

    @property
    def has_focus(self):
        return self._has_focus

    def __repr__(self):
        return "UIElement: {} ({})".format(self._name, type(self))


    def initialize(self):
        pass

    def finalize(self):
        pass


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

        self._caption_halign = kwargs.get('caption_halign', HorizontalAlignment.Left)
        self._caption_valign = kwargs.get('caption_valign', VerticalAlignment.Center)

        self._apply_font_style()

        self._text_caption = None
        self._text_bounds = None

        if self._show_caption and self._caption is not None:
            self._text_caption = self._font.render(self._caption, 1, self._font_colour)
            self._text_bounds = self._text_caption.get_rect()

            # we add a safety buffer around the text bounds to allow for the real bounds
            _w, _h = self._text_bounds[2] + 2 * I_MARGIN, self._text_bounds[3] + 2 * I_MARGIN
            if self.width is None or self.width < w:
                self.width = _w
            if self.height is None or self.height < h:
                self.height = _h

        self._surface = None
        if self.width is not None and self.height is not None:
            # TODO: we need to see about the correct surface flags to enable transparent control overlays
            self._surface = pygame.Surface((self.width, self.height))
        else:
            print("{}' surface was not initialized, because either width ({}) or height ({}) was not provided {}.".format(
                self._name, self.width, self.height, (w, h))
            )

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
        if self._invalidated:
            if self._surface is None:
                raise ValueError("Cannot paint into None surface: {}".format(self._name))

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
                # We place text in accordance with the chosen alignment.
                # This means vertically and horizontally, inside the parent's bounding box. The parent's
                # bounding box is at least so wide, so as to be able to capture the text.
                # It does not need to be recomputed every time - this can be placed after the initialization
                dest_pos = [0, 0]
                c_halign = self._caption_halign
                c_valign = self._caption_valign

                if c_halign == HorizontalAlignment.Left:
                    dest_pos[0] = I_MARGIN
                elif c_halign == HorizontalAlignment.Center:
                    dest_pos[0] = int(.5 * (self._w - self._text_bounds[2]))
                elif c_halign == HorizontalAlignment.Right:
                    dest_pos[0] = self._w - I_MARGIN - self._text_bounds[2]
                else:
                    raise ValueError("unknown horizontal alignment setting {}".format(c_halign))

                if c_valign == VerticalAlignment.Top:
                    dest_pos[1] = I_MARGIN
                elif c_valign == VerticalAlignment.Center:
                    dest_pos[1] = int(.5 * (self._h - self._text_bounds[3]))
                elif c_valign == VerticalAlignment.Bottom:
                    dest_pos[1] = self._h - I_MARGIN - self._text_bounds[3]
                else:
                    raise ValueError("unknown vertical alignment setting {}".format(c_valign))

                self._surface.blit(self._text_caption, dest=tuple(dest_pos))

            self._invalidated = False

    def render(self, buffer):
        # TODO: instead of asking are we invalidated in the render loop
        #   invalidation will call the paint call directly.
        #   every paint/ render pair needs to be check
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

    def on_click(self, sender, event_args):
        # when clicked this fires, it needs to be overwritten in a derived class
        pass


class Label(Renderable):
    """
    Label holding a single line of text
    """

    def __init__(self, name: str, x: int, y: int, caption: str, **kwargs):
        """Constructor for TextLabel"""
        if '\n' in caption:
            raise ValueError("Label does not support multiple lines of text")
        kwargs['caption'] = caption
        kwargs['show_caption'] = True

        if 'background_colour' not in kwargs:
            kwargs['background_colour'] = C_MENUGRAY

        if 'fill_style' not in kwargs:
            kwargs['fill_style'] = FillStyle.Colour

        if 'caption_halign' not in kwargs:
            kwargs['caption_halign'] = HorizontalAlignment.Left

        if 'caption_valign' not in kwargs:
            kwargs['caption_valign'] = VerticalAlignment.Center

        if 'colour' not in kwargs:
            kwargs['colour'] = C_ELEMENT_BORDER_DARKGRAY

        super(Label, self).__init__(name=name, x=x, y=y, **kwargs)


class MultiLineLabel(Label):
    """
    TODO: we need to ensure that the text breaks correctly.
    https://www.pygame.org/docs/ref/font.html
    The text can only be a single line: newline characters are not rendered.
    """

    def __init__(self, ):
        """Constructor for MultiLineLabel"""
        super(MultiLineLabel, self).__init__()

    def _paint(self):
        # TODO:
        if self._invalidated:
            self._invalidated = False
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

        raise ValueError("undefined item selected")

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


class Screen(Clickable):
    """
    The Screen type represents game windows, screens, overlays or anything similar.
    """

    def __init__(self, name: str, title: str, width: int, height: int, **kwargs):
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

    def paint(self):
        Clickable.paint(self)
        for _, ui_elem in self._components.items():
            if isinstance(ui_elem, Renderable):
                ui_elem.paint()

    def render(self, buffer):
        if self._invalidated:
            self._paint()

        Clickable.render(self, buffer)

        for _, ui_elem in self._components.items():
            if isinstance(ui_elem, Renderable):
                ui_elem.render(self._surface)

        buffer.blit(self._surface, (self._x0, self._y0))

    def unclick(self):
        Clickable.unclick(self)
        for _, c in self._components.items():
            if isinstance(c, Clickable):
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
            if isinstance(c, Clickable):
                is_clicked_i, sender_i = c.clicked(mx, my, button)
                if is_clicked_i:
                    is_clicked, sender = is_clicked_i, sender_i

        return is_clicked, sender


# TODO: GUI - the main gui manager
class WindowManager:
    """"""

    def __init__(self):
        """Constructor for GUI"""
        super(WindowManager, self).__init__()

        self._items = {}
        self._item_names = []
        self._transitions = {}
        self._active_screen = None

    @property
    def active_screen(self):
        return self._active_screen

    def add_screen(self, s:Screen, is_active:bool = False):
        if not s:
            raise ValueError("screen not provided")

        self._items[s.name] = s
        self._item_names.append(s.name)

        if is_active:
            self._active_screen = s

    def remove_screen(self, s_name:str):
        if not s_name:
            raise ValueError("screen not provided")

        # remove transitions and the actual screen ...
        to_remove = [k for k, v in self._transitions if v[0].name == s_name]
        for r in to_remove:
            del(self._transitions[r])

        del(self._items[s_name])
        self._item_names.remove(s_name)

    def transition(self, from_name, to_name):
        if not from_name:
            raise ValueError("from name missing")
        if not to_name:
            raise ValueError("to name missing")
        t_name = "{}-{}".format(from_name, to_name)
        from_screen, to_screen = self._transitions[t_name]
        from_screen.finalize()
        to_screen.initialize()
        self._active_screen = to_screen
        self.on_transitioned(from_screen, to_screen)

    def on_transitioned(self, from_name, to_name) -> None:
        """
        called after a transition is made
        :param from_name: old screen
        :param to_name:  target screen
        :return: None
        """
        return None

    def add_transition(self, from_screen: Screen, to_screen: Screen):
        if not from_screen:
            raise ValueError("from screen missing")
        if not to_screen:
            raise ValueError("to screen missing")
        t_name = "{}-{}".format(from_screen.name, to_screen.name)
        self._transitions[t_name] = (from_screen, to_screen)

    def remove_transition(self, from_name:str, to_name:str):
        if not from_name:
            raise ValueError("from name missing")
        if not to_name:
            raise ValueError("to name missing")
        t_name = "{}-{}".format(from_name, to_name)
        del(self._transitions[t_name])

    def __getitem__(self, item):
        if item is None:
            raise ValueError("getitem - key not provided")

        if isinstance(item, int):
            return self._items[self._item_names[item]]
        else:
            if item in self._items:
                return self._items[item]

        raise ValueError("Undefined screen selected")