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

    def sprite(self, sprite):
        self.sdl2_entity.sprite = sprite

    def __init__(self, controller, *args, **kwargs):
        pass


class ColorEntity(ClientEntity):
    def __init__(self, controller, color, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.color = color


class LabelEntity(ClientEntity):
    def __init__(self, controller, text, color, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.text = text
        self.color = color


class SelectionEntity(ColorEntity):
    def __init__(self, controller, color, *args, **kwargs):
        super().__init__(controller, color, *args, **kwargs)
        self.selected_index = 0
