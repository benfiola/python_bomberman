import common.entities as common_entities
import sdl2.ext


class Bomb(common_entities.Bomb, sdl2.ext.Entity):
    def __init__(self, entity):
        super().__init__()


class Player(common_entities.Player, sdl2.ext.Entity):
    def __init__(self, entity):
        super().__init__()


class IndestructableWall(common_entities.IndestructableWall, sdl2.ext.Entity):
    def __init__(self, entity):
        super().__init__()


class DestructableWall(common_entities.DestructableWall, sdl2.ext.Entity):
    def __init__(self, entity):
        super().__init__()


