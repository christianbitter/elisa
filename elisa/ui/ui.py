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
# UI element Button allows to have an image set.
# We make no distinction between clicked or not for now (which would justify an Image Button).
# todo: on mouse over event
# todo: on focus event
# todo: ui element label
# todo: support for rendering form with background and alpha blending of controls
# todo: having to forward the pygame event loop events to the controls is cumbersome, there
#   should be something cleaner
# todo: there should be something like overlays - where we have one form and can create smaller one blending it
#   over the existing one.
# todo: add unit testing
# todo: controls should have a global coordinate pair as well, this would simplify the hit-testing
# todo: screen transitions either in the screen or in the UI
# todo: initialization needs to be fixed, because for some ui elements we need to set fields that are used in the super
#       initialization routine
# TODO: rework
# TODO: allow specification of UI in a json file or something similar

import os
import pygame
import re
from enum import Enum, IntFlag

C_BLACK = (0, 0, 0, 255)
C_RED = (255, 0, 0, 255)
C_GREEN = (0, 255, 0, 255)
C_BLUE = (0, 0, 255, 255)
C_MENUGRAY = (192, 192, 192, 255)
C_FORMBLUE = (32, 32, 128, 255)
C_ELEMENT_BORDER_DARKGRAY = (64, 64, 64, 255)
C_WHITE = (255, 255, 255, 255)
C_BTN_FACE = (168, 168, 168, 255)
C_BTN_BORDER = (128, 128, 128, 255)
I_MARGIN = 3


def xy_inside(x: int, y: int, x0: int, y0: int, w: int, h: int) -> bool:
    return x0 <= x <= x0 + w and y0 <= y <= y0 + h


class UIEvent:
    SCREEN_TRANSITION:int = 99999

    @staticmethod
    def transition_screen(event_from:str, event_to:str):
        return pygame.event.Event(pygame.USEREVENT,
                                  {
                                      "mode": UIEvent.SCREEN_TRANSITION,
                                      "source": event_from,
                                      "target": event_to
                                  })


class FillStyle(Enum):
    Empty = 1
    Colour = 2
    Image = 3


class VerticalAlignment(Enum):
    Center = 0
    Top = 1
    Bottom = 2

    def __str__(self):
        return self.name


class HorizontalAlignment(Enum):
    Center = 0
    Left = 1
    Right = 2

    def __str__(self):
        return self.name


class FontStyle(IntFlag):
    """
    Style of a font
    """
    Normal = 0,
    Bold = 1,
    Italic = 2,
    Underline = 8

    def __str__(self):
        return self.name


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
        self._invalidated = kwargs.get('invalidated', False)
        self._has_focus = kwargs.get('has_focus', False)

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
        if w is None:
            raise ValueError("w cannot be None")
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
        if h is None:
            raise ValueError("h cannot be None")
        if h < 0:
            raise ValueError("h < 0")

        if self._h != h:
            self._h = h
            self._y1 = self._y0 + h
            self.invalidate()

    def invalidate(self, **kwargs):
        self._client_rect = (0, 0, self._w, self._h)
        self._invalidated = True

    def get_bounds(self):
        return self._x0, self._y0, self._x1, self._y1

    @property
    def has_focus(self):
        return self._has_focus

    @has_focus.setter
    def has_focus(self, f):
        self._has_focus = f

    def __repr__(self):
        return "UIElement: {} ({})".format(self._name, type(self))

    def initialize(self) -> None:
        pass

    def finalize(self) -> None:
        pass

    def update(self, t) -> None:
        pass

    def process_event(self, e) -> None:
        pass


class Renderable(UIElement):
    """
    The basic class for all ui renderable elements
    """

    def __init__(self, name, x: int = None, y: int = None, w: int = None, h: int = None, **kwargs):
        """Constructor for Renderable"""
        super().__init__(name, x=x, y=y, w=w, h=h, kwargs=kwargs)

        self._fill_style = kwargs.get('fill_style', FillStyle.Empty)
        self._background_colour = kwargs.get('background_colour', (128, 128, 128, 255))
        self._background_image = kwargs.get('background_image', None)
        self._colour = kwargs.get('colour', (0, 0, 0, 255))
        self._show_border = kwargs.get('show_border', True)
        self._show_caption = kwargs.get('show_caption', False)
        self._font_size = kwargs.get('font_size', 20)  # width and height is determined by font
        self._font_style = kwargs.get('font_style', FontStyle.Normal)
        self._font = pygame.font.Font(kwargs.get('font', pygame.font.get_default_font()), self._font_size)
        self._font_colour = kwargs.get('font_colour', C_BLACK)
        self._text_caption = None
        self._text_bounds = None
        self._caption = None
        self._surface = None

        self._caption = kwargs.get("caption", "")
        self.__update_caption()

        self._is_visible = kwargs.get('visible', True)
        self._z_order = kwargs.get('z', 0)

        self._caption_halign = kwargs.get('caption_halign', HorizontalAlignment.Left)
        self._caption_valign = kwargs.get('caption_valign', VerticalAlignment.Center)

        self._apply_font_style()

        if self.width is not None and self.height is not None:
            if self.width == 0 or self.height == 0:
                print("{} has set width and/or height to 0 px".format(self._name))
            self._surface = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        else:
            print("{}' surface was not initialized, because either width ({}) or height ({}) was not provided {}.".format(
                self._name, self.width, self.height, (w, h))
            )

        self.invalidate()

    def __update_caption(self):
        self._text_caption = self._font.render(self._caption, 1, self._font_colour)
        self._text_bounds = self._text_caption.get_rect()

        # we add a safety buffer around the text bounds to allow for the real bounds
        _w, _h = self._text_bounds[2] + 2 * I_MARGIN, self._text_bounds[3] + 2 * I_MARGIN
        if self.width is None or self.width < _w:
            self.width = _w
        if self.height is None or self.height < _h:
            self.height = _h

    def _apply_font_style(self):
        if self._font_style & FontStyle.Bold:
            self._font.set_bold(True)
        if self._font_style & FontStyle.Italic:
            self._font.set_italic(True)
        if self._font_style & FontStyle.Underline:
            self._font.set_underline(True)

    @property
    def z_order(self):
        return self._z_order

    @property
    def is_visible(self):
        return self._is_visible

    @property
    def background_colour(self):
        return self._background_colour

    @property
    def colour(self):
        return self._colour

    @property
    def show_border(self):
        return self._show_border

    def invalidate(self, **kwargs):
        UIElement.invalidate(self, **kwargs)
        # if we need to create a new surface we do otherwise we just clear
        if 'clear_only' in kwargs:
            self._surface.fill(C_BLACK)
        else:
            if self._w is not None and self._h is not None:
                # TODO: we need to see if we need per pixel alpha
                self._surface = pygame.Surface((self._w, self._h), flags=pygame.SRCALPHA)
                self._client_rect = (0, 0, self._w, self._h)

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, c):
        if c is None:
            return
        self._caption = c
        self.__update_caption()

    @property
    def show_caption(self):
        return self._show_caption

    def _paint(self):
        if self._invalidated:
            if self._surface is None:
                raise ValueError("Cannot paint into None surface: {}".format(self._name))

            if self._fill_style == FillStyle.Colour:
                pygame.draw.rect(self._surface, self._background_colour, self._client_rect, 0)
            elif self._fill_style == FillStyle.Image:
                if not self._background_image:
                    raise ValueError("background fill image but image not provided")

                scaled_bgimg = pygame.transform.scale(self._background_image, (self._w, self._h))
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

        if self._surface is None:
            raise ValueError("Failed _paint {} - surface is None.".format(self._name))

    def render(self, buffer):
        if self._invalidated:
            self._paint()
        if self._is_visible:
            buffer.blit(self._surface, (self.x, self.y))


class Clickable(Renderable):
    """"""

    def __init__(self, name, x: int = None, y: int = None, w: int = None, h: int = None, **kwargs):
        """Constructor for Clickable"""
        super().__init__(name, x=x, y=y, w=w, h=h, **kwargs)
        self._is_clicked = kwargs.get('is_clicked', False)

    def unclick(self):
        self._is_clicked = False

    def clicked(self, mx, my, button):
        previous_state = self._is_clicked
        if xy_inside(mx, my, self._x0, self._y0, self._w, self._h):
            self._is_clicked = True
        else:
            self._is_clicked = False

        # upon state change we invalidate
        if previous_state != self._is_clicked:
            self.invalidate()

        return self._is_clicked, self

    def on_click(self, sender, event_args):
        # when clicked this fires, it needs to be overwritten in a derived class
        pass


class UIImage(Clickable):
    """
    A component to show an image
    """

    def __init__(self, name: str, image_fp: str, x: int, y: int, w: int = None, h: int = None, **kwargs):
        """Constructor for UIImage"""
        if not image_fp or not os.path.exists(image_fp):
            raise ValueError("Image path not provided or does not exist")
        img = pygame.image.load(image_fp)
        rescale = False
        if w is None:
            w = img.get_width()
            rescale  = True
        if h is None:
            h = img.get_height()
            rescale = True
        s_img = pygame.transform.scale(img, (w, h))
        s = pygame.Surface((w, h))
        s.blit(s_img, (0, 0))
        del img
        kwargs['background_image'] = s
        kwargs['fill_style'] = FillStyle.Image
        self._image_fp = image_fp
        super(UIImage, self).__init__(name=name, x=x, y=y, w=w, h=h, **kwargs)

    def __repr__(self):
        return "[UIImage] {}: {}".format(self._name, self._image_fp)

    @property
    def image(self):
        return self._background_image

    @property
    def image_path(self):
        return self._image_fp

    def render(self, buffer):
        if self._invalidated:
            self._paint()
        Renderable.render(self, buffer)
        buffer.blit(self._background_image, (self._x0, self._y0, self.width, self.height))


class Canvas(Clickable):
    """
    A canvas is a simple renderable, which only exists for the purposes of drawing into it
    """

    def __init__(self, name: str, x: int, y: int, w: int, h: int, **kwargs):
        """Constructor for Canvas"""
        kwargs['show_border'] = False
        kwargs['show_caption'] = False
        super(Canvas, self).__init__(name=name, x=x, y=y, w=w, h=h, **kwargs)

    def render(self, buffer):
        if self.is_visible:
            return

        if self._invalidated:
            self._paint()

        buffer.blit(self._surface, (self.x, self.y))


class Label(Renderable):
    """
    Label holding a single line of text
    """

    def __init__(self, name: str, x: int, y: int, caption: str = None, **kwargs):
        """Constructor for TextLabel"""
        if caption is None:
            print("Caption ({}) cannot be none - set to empty string".format(name))
            caption = ''
        if os.linesep in caption:
            print("Label ({}) does not support multiple lines of text/ line breaks".format(name))

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


class TextBox(Label):
    """
    TODO: Text Box
    """

    __cursor__symbol = '|'

    __BLINK_ON__  = 1
    __BLINK_OFF__ = 0

    def __init__(self, name: str, x: int, y: int, max_chars: int = 20, w: int = 200, **kwargs):
        """Constructor for TextBox"""
        kwargs['show_border'] = True
        kwargs['background_colour'] = C_WHITE
        self._is_clicked = False
        self._blink_state = 0
        self._change_state_millis = 200
        self._dmillis = 0
        self._maxchars = max_chars
        self._cursor_added = False
        super(TextBox, self).__init__(name=name, x=x, y=y, w=w, **kwargs)

    @property
    def maxchars(self):
        return self._maxchars

    def update(self, t):
        if self._has_focus:
            self._dmillis += t

            if self._blink_state == TextBox.__BLINK_OFF__ and self._dmillis >= self._change_state_millis:
                self._blink_state = TextBox.__BLINK_ON__
                self._dmillis = 0

            if self._blink_state == TextBox.__BLINK_ON__ and self._dmillis >= self._change_state_millis:
                self._blink_state = TextBox.__BLINK_OFF__
                self._dmillis = 0

            self.invalidate()
        else:
            self._dmillis = 0
            self._blink_state = 0

    def clicked(self, mx, my, button):
        clicked, sender = Clickable.clicked(self, mx, my, button)
        if clicked:
            self.has_focus = True
        else:
            self.has_focus = False

        return clicked, sender

    def add_char(self, c) -> None:
        if len(self.caption) < self._maxchars:
            self.caption = self.caption + c

    def remove_char(self) -> None:
        l = len(self.caption)
        if l > 0:
            self.caption = self.caption[0:(l - 1)]

    def _paint(self):
        # add the blinking ...
        t_caption = self.caption
        if self._blink_state == 1:
            self.caption = self.caption + TextBox.__cursor__symbol
        Label._paint(self)
        self.caption = t_caption

    def process_event(self, e) -> None:
        if e.key == pygame.K_BACKSPACE:
            self.remove_char()

class MultiLineLabel(Label):
    """
    TODO MultiLineLabel - horizontal alignment
    TODO MultiLineLabel - vertical alignment
    TODO MultiLineLabel - new line handling - newline should be handled explicitly, when they are the single line element
    https://www.pygame.org/docs/ref/font.html
    The text can only be a single line: newline characters are not rendered.
    """

    def __init__(self, name: str, x: int, y: int, caption: str, **kwargs):
        """Constructor for MultiLineLabel"""
        w = kwargs.get('width', 200)
        kwargs['width'] = w
        kwargs['show_caption'] = False

        super(MultiLineLabel, self).__init__(name=name, x=x, y=y, caption=caption,  **kwargs)
        w_available = w - 2 * I_MARGIN

        self._lines = MultiLineLabel.split_text(self._font, text=caption, label_width=w_available)
        self._text_lines = [''.join(l).strip() for l in self._lines]
        x_i, y_i = x, y
        h_i = I_MARGIN
        for l_i in self._text_lines:
            s_i = self._font.render(l_i, 0, self._font_colour)
            h_i += s_i.get_height()
        h_i += I_MARGIN

        self.width = w
        self.height = h_i
        self.invalidate()

    @staticmethod
    def split_text(font, text: str, label_width: int):
        if font is None:
            raise ValueError("Font is not defined")
        if text is None:
            raise ValueError("Text is None")
        if label_width is None:
            raise ValueError("Label width is None")
        if label_width < 0:
            raise ValueError("Label width < 1")

        if text == '':
            return text
        frag_delim = '.,!?();:'
        s = text.strip()
        s = re.sub('([{}])'.format(frag_delim), r' \1 ', s)  # put space around the first match group
        s = re.sub('\s{2,}', ' ', s)  # collapse 2 white space characters into a single space

        # now simply split on space and get as many tokens into a line as possible
        s = re.split(r'(\s+)', s)
        sx = []
        for i, t in enumerate(s):
            if t == '':
                continue
            if t == os.linesep or t == '\n':
                t = ' '
            if i < len(s) - 1 and s[i] == ' ' and s[i + 1] in frag_delim:  # collapse ' ', '.' into '.'
                continue

            sx.append(t)
        s = sx

        temp_width = 0
        temp_sentence = []
        out_tokens = []

        # far and ask whether this is in the limits.
        for i, t in enumerate(s):
            r = font.render(t, 1, (0, 0, 0))
            w = r.get_width()
            # TODO: we do not put sentence delimiters as an opening token
            # still there is a breaking issue
            # instead we pull the last token of the previous line with it
            if temp_width + w >= label_width:
                # remove ending spaces from the temps
                x_sentence = temp_sentence.copy()
                l = len(x_sentence) - 1
                if x_sentence[l] == ' ':
                    x_sentence = x_sentence[0:l]
                if t in frag_delim:  # if t is a sentence/ fragement delimiter, we do not put on the next line
                    x_sentence.append(t)
                    t = None

                temp_sentence = []
                out_tokens.append(x_sentence)
                temp_width = 0

            if t is None:
                continue
            temp_sentence.append(t)
            temp_width += w

        if len(temp_sentence) > 0:
            out_tokens.append(temp_sentence)
        return out_tokens

    def _destpos_from_aligment(self, text_bounds):
        dest_pos = [0, 0]
        c_halign = self._caption_halign
        c_valign = self._caption_valign

        if c_halign == HorizontalAlignment.Left:
            dest_pos[0] = I_MARGIN
        elif c_halign == HorizontalAlignment.Center:
            dest_pos[0] = int(.5 * (self._w - text_bounds[2]))
        elif c_halign == HorizontalAlignment.Right:
            dest_pos[0] = self._w - I_MARGIN - text_bounds[2]
        else:
            raise ValueError("unknown horizontal alignment setting {}".format(c_halign))

        dest_pos[1] = I_MARGIN
        # TODO:
        # if c_valign == VerticalAlignment.Top:
        #     dest_pos[1] = I_MARGIN
        # elif c_valign == VerticalAlignment.Center:
        #     dest_pos[1] = int(.5 * (self._h - self._text_bounds[3]))
        # elif c_valign == VerticalAlignment.Bottom:
        #     dest_pos[1] = self._h - I_MARGIN - self._text_bounds[3]
        # else:
        #     raise ValueError("unknown vertical alignment setting {}".format(c_valign))
        return dest_pos

    def _paint(self):
        if self._surface is None:
            raise ValueError("Cannot paint into None surface: {}".format(self._name))
        if self._fill_style == FillStyle.Colour:
            pygame.draw.rect(self._surface, self._background_colour, self._client_rect, 0)
        elif self._fill_style == FillStyle.Image:
            if not self._background_image:
                raise ValueError("background fill image but image not provided")

            scaled_bgimg = pygame.transform.scale(self._background_image, (self._w, self._h))
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
            dst = self._destpos_from_aligment(self._client_rect)
            x_i = dst[0]
            y_i = I_MARGIN
            for s_i in self._text_lines:
                d_pos = [x_i, y_i]
                s_i = self._font.render(s_i, 0, self._font_colour)
                self._surface.blit(s_i, dest=tuple(d_pos))
                y_i += s_i.get_height()

        self._invalidated = False

    def render(self, buffer):
        if not self._show_caption and not self._show_border:
            return

        if self._invalidated:
            self._paint()

        buffer.blit(self._surface, (self.x, self.y))


class Button(Clickable):
    """
    A button is an element that can be clicked. It is in either of two states, clicked or not clicked.
    When the user clicks a button an event is fired and you may react to it.
    """

    def __init__(self, name, x: int, y: int, w: int = None, h: int = None, image_fp: str = None, **kwargs):
        """Constructor for Button"""
        # if we do have a caption but not an explicit show_caption, assume the default of show
        if 'caption' in kwargs and 'show_caption' not in kwargs:
            kwargs['show_caption'] = True
        if 'background_colour' not in kwargs:
            kwargs['background_colour'] = C_BTN_FACE
        if 'fill_style' not in kwargs:
            kwargs['fill_style'] = FillStyle.Colour
        if 'colour' not in kwargs:
            kwargs['colour'] = C_BTN_BORDER
        if image_fp is not None and os.path.exists(image_fp):
            kwargs['background_image'] = pygame.image.load(image_fp)
        super().__init__(name=name, x=x, y=y, w=w, h=h, **kwargs)

    def _paint(self):
        Clickable._paint(self)

        if self._is_clicked:
            pygame.draw.rect(self._surface, C_RED, self._client_rect, 2)


class MenuItem(Button):
    """"""

    def __init__(self, name: str, caption: str, w: int = None, h: int = None, **kwargs):
        """Constructor for MenuItem"""
        kwargs['caption'] = caption
        kwargs['show_caption'] = True
        kwargs['show_border'] = True
        kwargs['fill_style'] = FillStyle.Colour
        super().__init__(name=name, x=0, y=0, w=w, h=h, **kwargs)


class ClickableContainer(Clickable):
    """
    TODO: most of the menu stuff belongs into a clickable container
    """

    def __init__(self, name: str, x: int, y: int, w: int = None, h: int = None, **kwargs):
        """Constructor for ClickableContainer"""
        super(ClickableContainer, self).__init__(x=x, y=y, w=w, h=h)
        self._items = {}
        self._item_names = []
        self._iterm_inner_margin = kwargs.get('item_inner_margin', 2)


    @property
    def item_names(self):
        return self._item_names

    def __repr__(self):
        return "ClickableContainer: {} - {} items".format(self._name, len(self._item_names))

    @property
    def items(self):
        return self._items

    def __getitem__(self, item):
        if item is None:
            raise ValueError("getitem - key not provided")

        if isinstance(item, int):
            return self._items[self._item_names[item]]
        elif isinstance(item, str):
            if item in self._items:
                return self._items[item]
        else:
            self._items.get(item)

    def remove_item(self, item_name: str) -> None:
        """
        Remove an item from the items.
        :param item_name:
        :return: None
        """
        if item_name is None:
            raise ValueError("Item name not provided")
        if item_name not in self._item_names:
            raise ValueError("Item does not exist")

        # update item names and items
        del self._items[item_name]
        del self._item_names[self._item_names.index(item_name)]
        self.invalidate()

    def add_item(self, item, item_name: str):
        """
        Add an item to the existing items.
        :param item: the item to add
        :param item_name: (str) the item's name
        """
        if item is None:
            raise ValueError("Item not provided")
        if item_name is None:
            raise ValueError("Item name not provided")

        i_margin = self._iterm_inner_margin

        i_x = i_margin
        if len(self._item_names) < 1:  # first item
            if self._show_caption:
                i_y = i_margin + self._text_bounds[3]
            else:
                i_y = i_margin
            self.height = self.height + item.height
        else:
            last_item = self._items[self._item_names[len(self._item_names) - 1]]
            i_y = last_item.y + last_item.height + i_margin
            self.height = i_y + item.height + i_margin

        item.x = i_x
        item.y = i_y

        if item.width >= self.width:
            self.width = 2 * i_margin + item.width
            for _, mi in self._items.items():
                mi.width = item.width
        else:
            item.width = self.width - 2 * i_margin

        # now add and invalidate
        self._items[item_name] = item
        self._item_names.append(item_name)
        self.invalidate()


class Menu(Clickable):
    """
    A game menu - Single container.
    It does not support hotkeys, nesting and more common gui functionalty.
    TODO: reuse the clicable container.
    """
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
        :param mni: the menu item to add
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

    def __repr__(self):
        return "Menu: {} - {} items".format(self._name, len(self._item_names))

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
        # now ask for each item
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
        if not self._show_caption and not self._show_border and len(self._item_names) < 1:
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

    def _paint(self):
        Clickable._paint(self)
        for _, ui_elem in self._components.items():
            if isinstance(ui_elem, Renderable):
                ui_elem._paint()

    def render(self, buffer):
        """
        Renders the screen and all its associated components to the provided buffer
        :param buffer:
        :return:
        """
        if self._surface is None:
            raise ValueError("Cannot render {} - surface is none - check ui element creation.".format(self._name))
        if self._invalidated:
            self._paint()

        def can_render(o):
            return (isinstance(o, Renderable) and o.is_visible) or hasattr(o, 'render')

        def sorter(o):
            if hasattr(o, 'z_order'):
                return o.z_order
            else:
                return 0

        Clickable.render(self, buffer)
        # remove non-visible items and sort by z-index - front to back rendering
        ui_elems = [i for i in self._components.values() if can_render(i)]
        # sort by zindex
        visibles = sorted(ui_elems, key=sorter, reverse=False)
        for ui_elem in visibles:
            if isinstance(ui_elem, pygame.sprite.Sprite):
                ui_elem.draw()
                self._surface.blit(ui_elem.image, (ui_elem.rect[0], ui_elem.rect[1]))
            else:
                ui_elem.render(self._surface)

        buffer.blit(self._surface, (self._x0, self._y0))

    def unclick(self):
        Clickable.unclick(self)
        for _, c in self._components.items():
            if isinstance(c, Clickable):
                c.unclick()

    def __setitem__(self, key, value):
        if key in self._components:
            raise ValueError("item {} already added.".format(key))
        self._components[key] = value

    def update(self, t) -> None:
        if len(self._components) < 1:
            return

        for _, c in self._components.items():
            c.update(t)

    def add_component(self, c: UIElement) -> None:
        """
        Add a component to the screen's components
        :param c: (UIElement) the component to add
        :return: None
        """
        if not c:
            raise ValueError("component to add not provided")
        self._components[c.name] = c

    def remove_component(self, c_name: str):
        if not c_name:
            raise ValueError("component name is missing")

        del self._components[c_name]

    def __getitem__(self, item):
        if isinstance(item, str) and item in self._components:
            return self._components[item]

        if isinstance(item, int):
            if item < 0 or item >= len(self._components):
                raise ValueError("item index out of bounds")

            for j, c in enumerate(self._components):
                if j == item:
                    return c

        self._components.get(item)

    def clicked(self, mx, my, button):
        # check for self and all child elements if they are clicked the one with the smallest hitbox wins
        # if no child is clicked, see if we are clicked
        is_clicked, sender = Clickable.clicked(self, mx, my, button)

        for _, c in self._components.items():
            if isinstance(c, Clickable) or hasattr(c, 'clicked'):
                is_clicked_i, sender_i = c.clicked(mx, my, button)
                if is_clicked_i:
                    is_clicked, sender = is_clicked_i, sender_i

        return is_clicked, sender

    def process_event(self, e) -> None:
        # delegate an event to the control that is in focus
        # if there is no focused control, process it in the screen - swallow it
        for _, c in self._components.items():
            if c.has_focus:
                c.process_event(e)


class WindowManager:
    """
    # TODO: GUI - the main gui manager
    """

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

    def add_screen(self, s, is_active: bool = False):
        """
        Add a screen to the window manager's collection of screens
        :param s: (Screen) or list of (Screen) instances. If s is an individual screen the is_active flag can be
        used to set the screen to the default active screen. If multiple screens are passed as (list) object, then
        is_active is not used.
        :param is_active: (bool) sets the passed screen as the currently active screen
        :return: (None)
        """
        if not s:
            raise ValueError("screen not provided")

        if isinstance(s, Screen):
            self._items[s.name] = s
            self._item_names.append(s.name)

            if is_active:
                self._active_screen = s
        elif isinstance(s, list):
            for _screen in s:
                self._items[_screen.name] = _screen
                self._item_names.append(_screen.name)
        else:
            raise ValueError("Unknown type of s")

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

    # TODO: make into getter and setter
    def on_transitioned(self, from_name: str, to_name: str) -> None:
        """
        called after a transition is made
        :param from_name: old screen
        :param to_name:  target screen
        :return: None
        """
        return None

    def add_transition(self, from_screen: Screen, to_screen: Screen, add_reverse: bool = False):
        if not from_screen:
            raise ValueError("from screen missing")
        if not to_screen:
            raise ValueError("to screen missing")
        t_name = "{}-{}".format(from_screen.name, to_screen.name)
        self._transitions[t_name] = (from_screen, to_screen)

        if add_reverse:
            t_name = "{}-{}".format(to_screen.name, from_screen.name)
            self._transitions[t_name] = (to_screen, from_screen)

    def remove_transition(self, from_name: str, to_name: str):
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

    def update(self, t=None):
        self._active_screen.update(t)

    def process_event(self, e) -> None:
        return self.active_screen.process_event(e)
