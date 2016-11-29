class Spawn(object):
    def __init__(self, *args, **kwargs):
        pass

    def __eq__(self, other):
        return isinstance(other, Spawn) and other.__class__ == self.__class__


class PlayerSpawn(Spawn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IndestructableWallSpawn(Spawn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DestructableWallSpawn(Spawn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
