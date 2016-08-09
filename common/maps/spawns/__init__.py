

class EntitySpawn(object):
    def __init__(self, mapping, position):
        self.character_mapping = mapping
        self.position = position


class PlayerSpawn(EntitySpawn):
    def __init__(self, position=None):
        super().__init__('P', position)


class IndestructibleWallSpawn(EntitySpawn):
    def __init__(self, position=None):
        super().__init__('W', position)


class DestructibleWallSpawn(EntitySpawn):
    def __init__(self, position=None):
        super().__init__('D', position)

