import sdl2.ext
import uuid as uuid_lib


class SDL2Entity(sdl2.ext.Entity):
    def __init__(self, _):
        super().__init__()
        self.sprite = None
        self.animation = None


class ClientEntity(object):
    def __init__(self, controller, uuid=uuid_lib.uuid4(), view_qualifier=None):
        self._controller = controller
        self._uuid = uuid
        self._sdl2_entity = SDL2Entity(controller.world)
        self._sdl2_entity._id =uuid
        self._view_qualifier = view_qualifier
        self._controller.add_entity(self)
        self._initialized = True

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if getattr(self, "_initialized", False) and not key.startswith("_"):
            self._controller._on_entity_change(self, key, value)


class SelectionEntity(ClientEntity):
    def __init__(self, *args, **kwargs):
        self.selected_index = 0
        super().__init__(*args, **kwargs)


class MenuContainer(ClientEntity):
    def __init__(self, controller, entities, *args, **kwargs):
        self.entities = entities
        super().__init__(controller, *args, **kwargs)