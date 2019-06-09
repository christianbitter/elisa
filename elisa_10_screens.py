# desc:
# This implements a simple main screen with a single main menu.
# The main menu some entry - next.
# A screen can be clicked, all ui elements that are (of type) clickable in a screen can be clicked as well.
# When a clickable is clicked, a specific ui state is issued (clicked).
# When clicked the main entry, a new screen 'Next' loads. This screen has a single button 'back'.
# If the user clicks the button, she will be transported back to main menu. This continues until the user quits.
# TODO: support image as background in ui element - scaled to the appropriate dimensions if provided
# TODO: allow for different font styles - bold, italic, underlined

import os, sys
import pygame
from pygame import locals
from enum import Enum


def xy_inside(x:int, y:int, x0:int, y0:int, w:int, h:int) -> bool:
    return x0 <= x <= x0 + w and y0 <= y <= y0 + h


class UIElement(object):
    """"""

    def __init__(self, name, x:int = None, y:int = None, w:int = None, h:int = None, **kwargs):
        """Constructor for UIElement"""
        super().__init__()
        self._name = name
        self._x0 = x
        self._y0 = y
        self._x1 = None
        self._y1 = None
        if x and w:
            self._x1 = x + w
        if y and h:
            self._y1 = y + h
        self._w = w
        self._h = h

    @property
    def name(self):
        return self._name

    @property
    def x(self):
        return self._x0

    @property
    def y(self):
        return self._y0

    @property
    def width(self):
        return self._w

    @property
    def height(self):
        return self._h

    def get_bounds(self):
        return self._x0, self._y0, self._x1, self._y1

    def __repr__(self):
        return "UIElement: {} ({})".format(self._name, type(self))


class FillStyle(Enum):
    Empty = 1
    Colour = 2
    Image  = 3

class TextAlign(Enum):
    Center = 0
    Left=1
    Right=2

class Renderable(UIElement):
    """"""

    def __init__(self, name, x:int = None, y:int = None, w:int = None, h:int = None, **kwargs):
        """Constructor for Renderable"""
        super().__init__(name, x=x, y=y, w=w, h=h, kwargs=kwargs)
        self._fill_style        = kwargs.get('fill_style', FillStyle.Empty)
        self._background_colour = kwargs.get('background_colour', (128, 128, 128))
        self._background_image  = kwargs.get('background_image', None)
        self._colour = kwargs.get('colour', (0, 0, 0))
        self._show_border = kwargs.get('show_border', True)

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
        # print("FillStyle: ", self._fill_style)
        # print("Background Colour: ", self._background_colour)

        if self._fill_style == FillStyle.Colour:
            r = pygame.Rect(self._x0, self._y0, self._w, self._h)
            pygame.draw.rect(buffer, self._background_colour, r, 0)
        elif self._fill_style == FillStyle.Image:
            pass
        else:
            pass

        if self._show_border:
            r = pygame.Rect(self._x0, self._y0, self._w, self._h)
            pygame.draw.rect(buffer, self._colour, r, 1)


class Clickable(Renderable):
    """"""

    def __init__(self, name, x:int = None, y:int = None, w:int = None, h:int = None, **kwargs):
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

    def __init__(self, name, caption, x, y, w=0, h=0, **kwargs):
        """Constructor for Button"""
        self._caption = caption
        # width and height is determined by font
        self._font_size = kwargs.get('font_size', 20)
        self._font = pygame.font.Font(kwargs.get('font', pygame.font.get_default_font()), self._font_size)
        self._font_colour = kwargs.get('font_colour', (0, 0, 0))
        self._text_caption = self._font.render(caption, 1, self._font_colour)
        self._text_bounds = self._text_caption.get_rect()
        super().__init__(name, x=x, y=y, w=max(w, self._text_bounds[2]), h=max(h, self._text_bounds[3]), **kwargs)
        self._show_border = kwargs.get('show_border', False)
        self._caption = caption

    @property
    def caption(self):
        return self._caption

    def render(self, buffer):
        Renderable.render(self, buffer)

        if self._is_clicked:
            # draw a slight indent or something to indicate the clicking
            r = pygame.Rect(self._x0, self._y0, self._w, self._h)
            pygame.draw.rect(buffer, (0, 255, 0), r, 2)

        buffer.blit(self._text_caption, dest=(self._x0, self._y0, self._text_bounds[2], self._text_bounds[3]))


class MenuItem(Button):
    """"""
    def __init__(self, name:str, caption:str, x, y, **kwargs):
        """Constructor for MenuItem"""
        super().__init__(name, caption, x=x, y=y, **kwargs)


class Menu(Clickable):
    """"""

    def __init__(self, name, caption, x, y, **kwargs):
        """Constructor for Menu"""
        w, h = 5, 5  # some default, that will potentially be overwritten by sub items
        # if we show the caption, then we have to adjust the width and height right now
        self._caption = caption
        self._show_caption = kwargs.get('show_caption', False)

        super().__init__(name=name, x=x, y=y, w=w, h=h, **kwargs)

        self._items = []

    def add_item(self, m):
        # adding a menu item causes a potential update to the dimensions
        # we ask for the bounds of the child item and add some safety buffer
        i_x0, i_y0, i_x1, i_y1 = m.get_bounds()
        x1, y1 = self._x0 + self._w, self._y0 + self._h

        if i_x0 < self._x0: self._x0 = i_x0 - 5
        if i_y0 < self._y0: self._y0 = i_y0 - 5
        if i_x1 > x1: self._w = i_x1 - self._x0 + 5
        if i_y1 > y1: self._h = i_y1 - self._y0 + 5

        self._items.append(m)

    @property
    def caption(self):
        return self._caption

    @property
    def items(self):
        return self._items

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
        for m in self._items:
            m.render(buffer)

# TODO: a gamescreen is the container for our game, it can be a screen with a menu
# or a screen where there is full screen drawing
class GameScreen(Clickable):
    """"""
    def __init__(self, name, title, width, height, **kwargs):
        """Constructor for GameScreen"""
        super().__init__(name, x=0, y=0, w=width, h=height, **kwargs)
        self._title = title
        self._ui_elements = []

        self._initialize_components()

    def _initialize_components(self):
        pass

    def screen_transition(self):
        pass

    def render(self, buffer):
        buffer.fill(self._background_colour)

        for ui_elem in self._ui_elements:
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
        main_menu = Menu('menuMain', caption='Main', show_caption=False, x=50, y=100)
        menu_next = MenuItem(name='menuItemNext', caption='Next', x=55, y=105,
                             font_size=28, font_colour=(255, 255, 255))
        menu_next.on_click = self._menuitem_next_click

        main_menu.add_item(menu_next)
        main_menu.add_item(MenuItem(name='menuItemCredits', caption='Credits', x=55, y=130,
                                    font_size=28, font_colour=(255, 128, 64)))
        self._ui_elements.append(main_menu)

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
        self._ui_elements.append(buttonBack)

    def render(self, buffer):
        GameScreen.render(self, buffer)
        buffer.blit(self._header, (50, 50))


def main():

    if not pygame.font: print("Pygame - fonts not loaded")
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
