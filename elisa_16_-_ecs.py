# name: elisa_16_-_ecs.py
# auth: Christian Bitter
# desc:
# the starting of an entity-component-system. An entity component system is a system architectural style, by which object polymorphism is
# replaced through object composition. That is, instead of representing behavioural differences in entities through extension of the
# type hierarchy (e.g., Player->Knight, Angel, Devil), one works with a set of basic data elements (components) that mark and define these
# individual's differences - traits on individuals. For example, we might mark a Player with a "Devil" or "Angel" trait.
# Now, systems (environments if you will) exist that interpret these traits on individuals. For example, the DevilSystem would be used to
# manage all devils and the AngelSystem could manage all the intricacies of the angel entities.
# Sometimes it is necessary that angels and devils communicate, i.e. in that case messages are exchanged.
# for a german run down: see https://users.informatik.haw-hamburg.de/~abo781/abschlussarbeiten/ba_hanisch.pdf
# for an english source of information: https://www.randygaul.net/2013/05/20/component-based-engine-design/
#
# Now, in this example we are going to create a single entity elisa that can be situated in the game world. whenever the user presses the left or
# right key, elisa is moved left or right. Instead of the elisa visual of the past, this time we simply print elisa's position to the
# screen - a text renderer if you will.

import pygame
from uuid import uuid4


class ECSBase(object):
    def __init__(self):
        self._id = uuid4()


class Message(ECSBase):
    def __init__(self, msg_type):
        self._message_type = msg_type
        super(Message, self).__init__()

    def __repr__(self):
        return f"[Message/ {self._message_type}]: {self._id}"

    def __str__(self):
        return self.__repr__()


class UpdatePositionMessage(Message):
    def __init__(self, dx, dy):
        self._dx = dx
        self._dy = dy
        super(UpdatePositionMessage, self).__init__("UpdatePosition")


class Component(ECSBase):
    """[summary]
    A component is simply a collection of state that defines an entity in the game world. Components can bind properties
    like position, velocity or health.
    Args:
                    ECSBase ([type]): [description]
    """

    def __init__(self, component_type):
        self._component_type = component_type
        super(Component, self).__init__()

    def __repr__(self):
        return f"[Component/ {self._component_type}]: {self._id}"

    def __str__(self):
        return self.__repr__()


class Entity(ECSBase):
    """[summary]
    An entity is a named collection of components. You can add, remove, or search for components that the entity has registered. Additionally,
    entities can send messages to other entities and receive messages from other objects.
    """

    def __init__(self):
        self._components = dict()
        self._ctypes = dict()

        super(Entity, self).__init__()

    def add(self, c: Component):
        if not c:
            raise ValueError("No component provided")
        cid = str(c._id)
        if cid in self._components:
            raise ValueError("Component already exists")

        ctype = c._component_type
        self._components[str(c._id)] = c
        if ctype not in self._ctypes:
            self._ctypes[ctype] = {}
        dc = self._ctypes[ctype]
        dc[cid] = c

    def has_component_type(self, component_type):
        if not component_type or component_type == "":
            raise ValueError("component_type not provided")

        return component_type in self._ctypes

    def remove(self, component_id: str):
        if not component_id or component_id == "":
            raise ValueError("No component id provided")

        if component_id in self._components:
            ctype = self._components[component_id]._component_type
            delattr(self._components, component_id)
            delattr(self._ctypes[ctype], component_id)

    def __getitem__(self, key):
        if isinstance(key, int):
            if key > len(self._components):
                raise ValueError("index outside of registered components")
            for i, k in enumerate(self._components):
                if i == key:
                    return self._components[k]
        else:
            return self._components[key]

    def send_msg(self, msg):
        pass

    def __repr__(self):
        c_str = f"Entity: {self._id}\r\n"
        if len(self._components) == 0:
            c_str += "No registered components"
        else:
            for i, k in enumerate(self._components):
                c_str += "[+{}] = {}\r\n".format(i, self._components[k])
        return c_str

    def __str__(self):
        return self.__repr__()


class AgentEntity(Entity):
    def __init__(self):
        super(AgentEntity, self).__init__()

    def _handle_position_update_(self, dx, dy):
        if "Position" in self._ctypes:
            position_comps = self._ctypes["Position"]
            for k in position_comps:
                position_comps[k].x += dx
                position_comps[k].y += dy

        return None

    def send_msg(self, msg):
        return {"PositionUpdate": self._handle_position_update_(msg._dx, msg._dy)}.get(
            msg._message_type, None
        )


class CharacterComponent(Component):
    """[summary]
    The CharacterComponent is a simple component, that associates an entity with a name.
    Args:
                    Component ([type]): [description]
    """

    def __init__(self, name):
        self.name = name
        super(CharacterComponent, self).__init__("Character")

    def __repr__(self):
        return f"Name = {self.name}"


class PositionComponent(Component):
    """[summary]
    The PositionComponent is a simple component that associates an entity with a 2D position.
    Args:
                    Component ([type]): [description]
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        super(PositionComponent, self).__init__("Position")

    def __repr__(self):
        return f"Position(x, y) = ({self.x}, {self.y})"


class System(ECSBase):
    def __init__(self):
        super(System, self).__init__()

    def update(self, time_delta, entities):
        pass

    def send_msg(self, msg):
        pass

    def receive_msg(self, msg):
        pass


class InputSystem(System):
    def __init__(self):
        super(InputSystem, self).__init__()

    def update(self, time_delta, entities):
        key_map = pygame.key.get_pressed()

        if key_map[pygame.K_LEFT]:
            # let's move all entities with a position component to the left
            position_entities = [
                e for e in entities if e.has_component_type("Position")
            ]

            upos = UpdatePositionMessage(dx=-1, dy=0)
            for pe in position_entities:
                # send the update position message
                pe.send_msg(upos)

        if key_map[pygame.K_RIGHT]:
            position_entities = [
                e for e in entities if e.has_component_type("Position")
            ]
            print("Found {} entities with position.".format(len(position_entities)))

            upos = UpdatePositionMessage(dx=+1, dy=0)
            for pe in position_entities:
                # send the update position message
                pe.send_msg(upos)

    def send_msg(self, msg):
        return super().send_msg(msg)

    def receive_msg(self, msg):
        return super().receive_msg(msg)


class RenderSystem(System):
    """[summary]
    This is a very simple render system, we are simply going to output the current position of the relevant entities. For that,
    we do not really need a very elaborate visual component, but rather make use of the PositionComponent.
    Args:
                    System ([type]): [description]
    """

    def __init__(self):
        super(RenderSystem, self).__init__()

    def update(self, time_delta, entities):
        if len(entities) < 1:
            return None
        # With only one entity in place we are not going to bother but render all entities
        for e in entities:
            print(e)

        return None

    def send_msg(self, msg):
        return super().send_msg(msg)

    def receive_msg(self, msg):
        return super().receive_msg(msg)


def main():
    if not pygame.font:
        print("Pygame - fonts not loaded")
    if not pygame.mixer:
        print("Pygame - audio not loaded")

    # create the main entity
    elisa = AgentEntity()
    elisa.add(CharacterComponent("elisa"))
    elisa.add(PositionComponent(1, 1))
    print(elisa)
    i = 1
    print(f"Component at index {i} = {elisa[i]}")

    # create a system to handle input and rendering
    input_sys = InputSystem()
    render_sys = RenderSystem()

    pygame.init()
    w, h, t = 640, 480, "Elisa - 16 Entities, Components, and Systems"
    is_done = False
    fps_watcher = pygame.time.Clock()

    screen_buffer = pygame.display.set_mode(size=(w, h))
    pygame.display.set_caption(t)
    pygame.mouse.set_visible(True)

    back_buffer: pygame.Surface = pygame.Surface(
        screen_buffer.get_size(), pygame.SRCALPHA
    )

    # for now we simply manage one entity
    entities = [elisa]

    while not is_done:
        elapsed_millis = fps_watcher.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_done = True
                break

            input_sys.update(time_delta=elapsed_millis, entities=entities)
            render_sys.update(time_delta=elapsed_millis, entities=entities)

        if not is_done:
            screen_buffer.blit(back_buffer, (0, 0))
            pygame.display.flip()


if __name__ == "__main__":
    main()
