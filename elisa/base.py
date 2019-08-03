# TODO: when reworking the individual definitions into reusable modules and classes
#       the base type of many of them will be entity.
#       In the tutorial mode, this is not as strict


import uuid

class ECSObject(object):
    """
    """
    def __init__(self, name: str, ecstype: str):
        super(ECSObject, self).__init__()
        self._uid = uuid.uuid4()
        self._name = name
        self._ecstype = ecstype

    @property
    def ecstype(self):
        return self._ecstype

    @property
    def name(self):
        return self._name

    @property
    def uid(self):
        return self._uid


class Component(ECSObject):
    """
    """
    def __init__(self, name: str, ctype: str):
        ECSObject(Component, self).__init__(name=name, ecstype=ctype)

    def __repr__(self):
        return "Component-{}[{}]: {}".format(self._ecstype, self._uid, self._name)


class Entity(ECSObject):
    """
    """
    def __init__(self, name: str, etype: str):
        ECSObject(Component, self).__init__(name=name, ecstype=etype)

    def __repr__(self):
        return "Entity-{}[{}]: {}".format(self._ecstype, self._uid, self._name)


class ECSystem(ECSObject):
    """
    """
    def __init__(self, name: str, systype: str):
        ECSObject(Component, self).__init__(name=name, ecstype=systype)

    def __repr__(self):
        return "EntityComponentSystem-{}[{}]: {}".format(self._ecstype, self._uid, self._name)
