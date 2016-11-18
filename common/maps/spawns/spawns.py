class Spawn(object):
    def __init__(self, *args, **kwargs):
        pass


class PlayerSpawn(Spawn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IndestructableWallSpawn(Spawn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DestructableWallSpawn(Spawn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
