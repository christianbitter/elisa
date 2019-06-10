# desc:
# This implements a simple main screen with a single main menu.
# The main menu some entry - next.
# A screen can be clicked, all ui elements that are (of type) clickable in a screen can be clicked as well.
# When a clickable is clicked, a specific ui state is issued (clicked).
# When clicked the main entry, a new screen 'Next' loads. This screen has a single button 'back'.
# If the user clicks the button, she will be transported back to main menu. This continues until the user quits.
# A renderable can have a caption text. The text can be styled differently - bold, italic, underlined.

import pygame
from enum import Enum, IntFlag
from sprites import SpriteMap


def xy_inside(x:int, y:int, x0:int, y0:int, w:int, h:int) -> bool:
    return x0 <= x <= x0 + w and y0 <= y <= y0 + h


class FillStyle(Enum):
    Empty = 1
    Colour = 2
    Image  = 3


class TextAlign(Enum):
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

    def __init__(self, name, x:int = None, y:int = None, w: int = None, h: int = None, **kwargs):
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

    @property
    def name(self):
        return self._name

    @property
    def x(self):
        return self._x0

    @x.setter
    def x(self, x:int):
        if not x:
            raise ValueError("x")
        if x < 0:
            raise ValueError("x < 0")
        self._x0 = x
        self._x1 = self._x0 + self._w

    @property
    def y(self):
        return self._y0

    @y.setter
    def y(self, y:int):
        if not y:
            raise ValueError("y")
        if y < 0:
            raise ValueError("y < 0")
        self._y0 = y
        self._y1 = self._y0 + self._h

    @property
    def width(self):
        return self._w

    @width.setter
    def width(self, w):
        if not w:
            raise ValueError("w")
        if w < 0:
            raise ValueError("w < 0")
        self._w = w
        self._x1 = self._x0 + w

    @property
    def height(self):
        return self._h

    @height.setter
    def height(self, h: int = None):
        if not h:
            raise ValueError("h")
        if h < 0:
            raise ValueError("h < 0")
        self._h = h
        self._y1 = self._y0 + h

    def get_bounds(self):
        return self._x0, self._y0, self._x1, self._y1

    def __repr__(self):
        return "UIElement: {} ({})".format(self._name, type(self))


class Renderable(UIElement):
    """"""

    def __init__(self, name, x: int = None, y: int = None, w: int = None, h: int = None, **kwargs):
        """Constructor for Renderable"""
        super().__init__(name, x=x, y=y, w=w, h=h, kwargs=kwargs)

        self._fill_style        = kwargs.get('fill_style', FillStyle.Empty)
        self._background_colour = kwargs.get('background_colour', (128, 128, 128))
        self._background_image  = kwargs.get('background_image', None)
        self._colour = kwargs.get('colour', (0, 0, 0))
        self._show_border = kwargs.get('show_border', True)

        self._caption = kwargs.get("caption", "")
        self._font_size = kwargs.get('font_size', 20)  # width and height is determined by font
        self._font_style = kwargs.get('font_style', FontStyle.Normal)
        self._font = pygame.font.Font(kwargs.get('font', pygame.font.get_default_font()),
                                      self._font_size)
        self._font_colour = kwargs.get('font_colour', (0, 0, 0))

        self._apply_font_style()

        self._text_caption = None
        self._text_bounds = None

        if self._caption is not None:
            self._text_caption = self._font.render(self._caption, 1, self._font_colour)
            self._text_bounds = self._text_caption.get_rect()
            # we add a safety buffer around the text bounds to allow for the real bounds
            w, h = self._text_bounds[2] + 3, self._text_bounds[3] + 3
            if not self.width or self.width < w:
                self.width = w
            if not self.height or self.height < h:
                self.height = h

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

    def render(self, buffer):
        r = pygame.Rect(self._x0, self._y0, self._w, self._h)
        if self._fill_style == FillStyle.Colour:
            pygame.draw.rect(buffer, self._background_colour, r, 0)
        elif self._fill_style == FillStyle.Image:
            if not self._background_image:
                raise ValueError("background fill image but image not provided")

            scaled_bgimg = pygame.transform.scale(self._background_image.image, (self._w, self._h))
            buffer.blit(scaled_bgimg, dest=(self._x0, self._y0, self._w, self._h))
        else:
            pass

        if self._show_border:
            r = pygame.Rect(self._x0, self._y0, self._w, self._h)
            pygame.draw.rect(buffer, self._colour, r, 1)

        if self._caption:
            buffer.blit(self._text_caption, dest=(self._x0, self._y0, self._text_bounds[2], self._text_bounds[3]))


class Clickable(Renderable):
    """"""

    def __init__(self, name, x: int = None, y: int = None, w: int = None, h: int = None, **kwargs):
        """Constructor for Clickable"""
        super().__init__(name, x=x, y=y, w=w, h=h, **kwargs)
        self._is_clicked = False

    def unclick(self):
        self._is_clicked = False

    def clicked(self, mx, my, button):
        if xy_inside(mx, my, self._x0, self._y0, self._w, self._h):
            self._is_clicked = True
        else:
            self._is_clicked = False

        return self._is_clicked, self

    def on_click(self, sender, x, y, button):
        # when clicked this fires, it needs to be overwritten in a derived class
        pass

    def render_clicked(self, buffer):
        pass

    def render_unclicked(self, buffer):
        pass

    def render(self, buffer):
        if self._is_clicked:
            self.render_clicked(buffer)
        else:
            self.render_unclicked(buffer)


class Button(Clickable):
    """"""

    def __init__(self, name, caption, x: int, y: int, w: int = None, h: int = None, **kwargs):
        """Constructor for Button"""
        super().__init__(name=name, caption=caption, x=x, y=y, w=w, h=h, **kwargs)

    @property
    def caption(self):
        return self._caption

    def render(self, buffer):
        Renderable.render(self, buffer)

        if self._is_clicked:
            # draw a slight indent or something to indicate the clicking
            r = pygame.Rect(self._x0, self._y0, self._w, self._h)
            pygame.draw.rect(buffer, (0, 255, 0), r, 2)


class MenuItem(Button):
    """"""
    def __init__(self, name:str, caption: str, w:int = None, h: int = None, **kwargs):
        """Constructor for MenuItem"""
        super().__init__(name=name, caption=caption, x=0, y=0, w=w, h=h, **kwargs)


class Menu(Clickable):
    """"""
    MENU_ITEM_INNER_MARGIN = 3

    def __init__(self, name, caption, x, y, **kwargs):
        """Constructor for Menu"""
        super().__init__(name=name, x=x, y=y, w=5, h=5, **kwargs)
        self._items = {}
        self._item_names = []

    def add_item(self, m: MenuItem):
        """
        Add a menu item to the existing menu items.
        :param m: the menu item to add
        """
        if not m:
            raise ValueError("No Item to add")

        i_margin = Menu.MENU_ITEM_INNER_MARGIN
        # adding a menu item causes a potential update to the dimensions
        # we ask for the bounds of the child item and add some safety buffer
        i_x0, i_y0, i_x1, i_y1 = m.get_bounds()
        i_w, i_h = i_x1 - i_x0, i_y1 - i_y0

        # where to start placing the item
        i_x0, i_y0 = self._x0 + i_margin, self._y0 + i_margin
        i_x1, i_y1 = i_margin + i_w, i_margin + i_h

        if len(self._item_names) >= 1:
            last_item = self._items[self._item_names[len(self._item_names) - 1]]
            l_x0, _, _, l_y1 = last_item.get_bounds()
            i_x0, i_x1 = l_x0, l_x0 + i_w
            i_y0, i_y1 = l_y1 + 1, l_y1 + 1 + i_h

        m.x = i_x0
        m.y = i_y0

        x1, y1 = self._x0 + self._w, self._y0 + self._h

        # all menu items are placed inside the margins of the menu
        if i_x1 > x1:
            self._w = i_x1 - self._x0 + i_margin
        if i_y1 > y1:
            self._h = i_y1 - self._y0 + i_margin

        self._items[m.name] = m
        self._item_names.append(m.name)

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

    @property
    def show_caption(self):
        return self._show_caption

    def unclick(self):
        Clickable.unclick(self)
        for c in self._items:
            c.unclick()

    def clicked(self, mx, my, button):
        # we do not focus on the right button
        is_clicked, sender = Clickable.clicked(self, mx, my, button)

        for c in self._items:
            is_clicked_i, sender_i = c.clicked(mx, my, button)
            if is_clicked_i:
                is_clicked, sender = is_clicked_i, sender_i

        return is_clicked, sender

    def render(self, buffer):
        #  collect the bounds if any and draw the bounding element
        x0, y0, w, h = self._x0, self._y0, self._w, self._h
        r = pygame.Rect(x0, y0, w, h)
        pygame.draw.rect(buffer, self._colour, r, 1)

        # render all the items
        for _, m in self._items.items():
            m.render(buffer)


class GameScreen(Clickable):
    """"""
    def __init__(self, name, title, width, height, **kwargs):
        """Constructor for GameScreen"""
        super().__init__(name, x=0, y=0, w=width, h=height, **kwargs)
        self._title = title
        self._components = {}

        self._initialize_components()

    def _initialize_components(self):
        pass

    def screen_transition(self):
        pass

    def render(self, buffer):
        buffer.fill(self._background_colour)

        for _, ui_elem in self._components.items():
            if isinstance(ui_elem, Renderable):
                ui_elem.render(buffer)

    def unclick(self):
        Clickable.unclick(self)
        for c in self._ui_elements:
            c.unclick()

    def clicked(self, mx, my, button):
        # check for self and all child elements if they are clicked the one with the smallest hitbox wins
        # if no child is clicked, see if we are clicked
        is_clicked, sender = Clickable.clicked(self, mx, my, button)
            
        for c in self._ui_elements:
            is_clicked_i, sender_i = c.clicked(mx, my, button)
            if is_clicked_i:
                is_clicked, sender = is_clicked_i, sender_i

        return is_clicked, sender


class MainScreen(GameScreen):
    """"""

    def __init__(self):
        """Constructor for MainScreen"""
        super().__init__(name='screenMain', title='Main', width=640, height=480)
        text = "Elisa 10 - Main Screen"
        self._font = pygame.font.Font(pygame.font.get_default_font(), 32)
        self._header = self._font.render(text, 1, (64, 0, 255))

    def _menuitem_next_click(self, sender, x, y, button):
        self.screen_transition(self)

    def _initialize_components(self):
        grass_sprite_map = SpriteMap("asset/tileset_grass.json")
        grass_sprite_map.initialize()
        img = grass_sprite_map['grass_2']

        main_menu = Menu('menuMain', caption='Main', show_caption=False, x=50, y=100)
        menu_next = MenuItem(name='menuItemNext', caption='Next',
                             font_size=28, font_colour=(255, 255, 255),
                             font_style=FontStyle.Bold | FontStyle.Italic | FontStyle.Underline)
        menu_next.on_click = self._menuitem_next_click
        main_menu.add_item(menu_next)

        main_menu.add_item(MenuItem(name='menuItemCredits', caption='Credits', font_size=28, font_colour=(255, 128, 64)))

        main_menu.add_item(MenuItem(name='menuItemGFX', caption='', font_size=28, font_colour=(255, 128, 64),
                                    background_image = img, show_border=True, fill_style=FillStyle.Image,
                                    w=main_menu["menuItemCredits"].width, h=main_menu["menuItemCredits"].height
                                    ))
        self._components[main_menu.name] = main_menu

    def render(self, buffer):
        GameScreen.render(self, buffer)
        buffer.blit(self._header, (50, 50))


class NextScreen(GameScreen):
    """"""

    def __init__(self):
        """Constructor for NextScreen"""
        super().__init__(name='screenNext', title='Next', width=640, height=480)
        text = "Elisa 10 - Next Screen"
        self._font = pygame.font.SysFont('comicsansms', 32)
        self._header = self._font.render(text, True, (64, 0, 255))

    def _button_back_click(self, sender, x, y, button):
        self.screen_transition(self)

    def _initialize_components(self):
        buttonBack = Button('buttonBack', 'back', x=300, y=200, # w=100, h=32, - the alignment is not fixed
                            background_colour=(92, 92, 92), fill_style=FillStyle.Colour)
        buttonBack.on_click = self._button_back_click
        self._components[buttonBack.name] = buttonBack

    def render(self, buffer):
        GameScreen.render(self, buffer)
        buffer.blit(self._header, (50, 50))


def main():

    if not pygame.font: raise("Pygame - fonts not loaded")
    if not pygame.mixer: print("Pygame - audio not loaded")

    # init pygame - create the main window, and a background surface

    pygame.init()

    S_WIDTH = 640
    S_HEIGHT= 480
    S_TITLE = "Elisa 10 - A Simple Screen/ Scene/ Menu Structure"

    screen_buffer = pygame.display.set_mode(size=(S_WIDTH, S_HEIGHT))
    pygame.display.set_caption(S_TITLE)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(screen_buffer.get_size())
    back_buffer = back_buffer.convert()
    back_buffer.fill((250, 250, 250))

    main_screen = MainScreen()
    next_screen = NextScreen()

    screens = [main_screen]
    active_screen = screens[0]

    # probably not the most elegent way, but what the heck
    def screen_transition(self, from_screen, to_screen):
        def screen_transition_internal(self):
            screens.pop(0)
            screens.insert(0, to_screen)
        return screen_transition_internal

    next_screen.screen_transition = screen_transition(next_screen, next_screen, main_screen)
    main_screen.screen_transition = screen_transition(main_screen, main_screen, next_screen)
    # FPS watcher
    fps_watcher = pygame.time.Clock()
    is_done = False

    while not is_done:
        fps_watcher.tick(60)
        active_screen = screens[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y =  event.pos[0], event.pos[1]
                    clicked, sender = active_screen.clicked(mx=x, my=y, button=event.button)
                    if clicked:
                        sender.on_click(sender=sender, x=x, y=y, button=event.button)
                if event.type == pygame.MOUSEBUTTONUP:
                    active_screen.unclick()

                active_screen.render(back_buffer)
                screen_buffer.blit(back_buffer, (0, 0))
                pygame.display.flip()

if __name__ == '__main__': main()
