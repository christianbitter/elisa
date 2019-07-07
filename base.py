# TODO: when reworking the individual definitions into reusable modules and classes
#       the base type of many of them will be entity.
#       In the tutorial mode, this is not as strict
class Entity(object):
    """"""

    def __init__(self, id, the_type:str, **kwargs):
        """Constructor for Entity"""
        super(Entity, self).__init__()
        self._id = id
        self._type = the_type
        self._properties = kwargs.copy()

    def serialize(self):
        pass

    def deserialize(self):
        pass

    @property
    def id(self):
        return self._id

    @property
    def entity_type(self):
        return self._type

    def __repr__(self):
        return "[{}] {}".format(self._type, self._id)
