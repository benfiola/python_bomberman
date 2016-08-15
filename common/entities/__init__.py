import uuid


class Entity(object):
    def __init__(self, position):
        self.id = uuid.uuid4()
        self.position = position
        self.sprite = None


class PlayerEntity(Entity):
    def __init__(self, position):
        super().__init__(position)


class DestructibleWallEntity(Entity):
    def __init__(self, position):
        super().__init__(position)


class IndestructibleWallEntity(Entity):
    def __init__(self, position):
        super().__init__(position)