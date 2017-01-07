import sdl2.ext
import uuid


class SDL2Entity(sdl2.ext.Entity):
    def __init__(self, world):
        super().__init__()
        self.sprite = None
        self.velocity = None


class ClientEntity(object):
    def __new__(cls, controller, *args, **kwargs):
        _uuid = uuid.uuid4()
        if "uuid" in kwargs:
            _uuid = kwargs["uuid"]

        entity = object.__new__(cls)
        entity.controller = controller
        entity.uuid = _uuid
        entity._controller = controller
        entity._uuid = _uuid
        entity.sdl2_entity = SDL2Entity(controller.world)
        entity.controller.add_entity(entity)

        return entity

    def __init__(self, controller, *args, **kwargs):
        if "sprite" in kwargs:
            self.sdl2_entity.sprite = kwargs["sprite"]
            if "position" in kwargs:
                self.sdl2_entity.sprite.position = kwargs["position"]


class BackgroundEntity(ClientEntity):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)


class LabelEntity(ClientEntity):
    def __init__(self, controller, text, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.text = text


class SelectionEntity(ClientEntity):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.selected_index = 0
