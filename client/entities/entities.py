import sdl2.ext
import uuid as uuid_lib


class SDL2Entity(sdl2.ext.Entity):
    def __init__(self, _):
        super().__init__()
        self.sprite = None
        self.animation = None


class ClientEntity(object):
    def __new__(cls, controller, uuid=uuid_lib.uuid4(), view_qualifier=None, *args, **kwargs):
        _uuid = uuid_lib.uuid4()
        if "uuid" in kwargs:
            _uuid = kwargs["uuid"]

        entity = object.__new__(cls)
        entity._controller = controller
        entity._uuid = _uuid
        entity._sdl2_entity = SDL2Entity(controller.world)
        entity._sdl2_entity._id = _uuid
        entity._view_qualifier = view_qualifier
        entity._controller.add_entity(entity)
        return entity

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if not key.startswith("_"):
            self._controller._on_entity_change(self, key, value)


class SelectionEntity(ClientEntity):
    def __init__(self, _, *args, **kwargs):
        self.selected_index = 0
