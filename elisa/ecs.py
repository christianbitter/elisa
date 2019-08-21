import uuid


class Entity(object):
    """
    A simple entity in the ECS world
    """
    __slots__ = ['_id', '_name', '_components']

    def __init__(self, name: str):
        """Constructor for Entity"""
        super(Entity, self).__init__()
        self._name = name
        self._id = uuid.uuid4()
        self._components = {}

    def __getitem__(self, item):
        if isinstance(item, int):
            if item < 0 or item > len(self._components):
                raise ValueError("item out of bounds")
            for i, e in enumerate(self._components.items()):
                if i == item:
                    return e
        elif isinstance(item, str):
            return self._components[item]
        else:
            return self._components.get(item)

    def __setitem__(self, key, value):
        self._components[key] = value

    def __getattr__(self, item):
        pass

    def __setattr__(self, key, value):
        pass

    def __iter__(self):
        return self._components

    def __len__(self):
        return len(self._components)
