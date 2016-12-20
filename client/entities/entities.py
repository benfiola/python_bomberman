import common.entities as common_entities
import client.graphics as graphics
import sdl2.ext
import uuid


class ClientEntity(sdl2.ext.Entity):
    def __init__(self, world, uuid):
        self.uuid = uuid


class BackgroundEntity(ClientEntity):
    def __init__(self, world, sprite, position, uuid=uuid.uuid4()):
        super().__init__(world, uuid)
        self.sprite = sprite
        self.sprite.position = position


class LabelEntity(ClientEntity):
    def __init__(self, world, text, sprite, position, uuid=uuid.uuid4()):
        super().__init__(world, uuid)
        self.text = text
        self.sprite = sprite
        self.sprite.position = position


class SelectionEntity(ClientEntity):
    def __init__(self, world, sprite, position, uuid=uuid.uuid4()):
        super().__init__(world, uuid)
        self.sprite = sprite
        self.sprite.position = position
        self.selected_index = 0


class Bomb(common_entities.Bomb, sdl2.ext.Entity):
    def __init__(self, sprite, position, world=None):
        super().__init__()


class Player(common_entities.Player, sdl2.ext.Entity):
    def __init__(self, sprite, position, world=None):
        super().__init__()


class IndestructableWall(common_entities.IndestructableWall, sdl2.ext.Entity):
    def __init__(self, sprite, position, world=None):
        super().__init__()


class DestructableWall(common_entities.DestructableWall, sdl2.ext.Entity):
    def __init__(self, sprite, position, world=None):
        super().__init__()


