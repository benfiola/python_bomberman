import uuid, time


class Entity(object):
    def __init__(self, position):
        self.id = uuid.uuid4()
        self.position = position
        self.sprite = None


class PlayerEntity(Entity):
    def __init__(self, position):
        super().__init__(position)


class BombEntity(Entity):
    DURATION = 5.0
    RADIUS = 2

    def __init__(self, position):
        super().__init__(position)
        self.time_placed = time.time()


class FireEntity(Entity):
    DURATION = 1.0
    def __init__(self, position):
        super().__init__(position)
        self.time_placed = time.time()


class DestructibleWallEntity(Entity):
    def __init__(self, position):
        super().__init__(position)


class IndestructibleWallEntity(Entity):
    def __init__(self, position):
        super().__init__(position)