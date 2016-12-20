import uuid


class Entity(object):
    def __init__(self, uuid=uuid.uuid4()):
        self.uuid = uuid


class Player(Entity):
    def __init__(self):
        super().__init__()


class IndestructableWall(Entity):
    def __init__(self):
        super().__init__()


class DestructableWall(Entity):
    def __init__(self):
        super().__init__()


class Bomb(Entity):
    def __init__(self):
        super().__init__()

