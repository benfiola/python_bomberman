from client.graphics.views import *


class SinglePlayerView(View):
    BACKGROUND = "background"
    GAME_CONTAINER = "game-container"
    BOMB = "bomb"
    PLAYER = "player"
    DESTRUCTIBLE_WALL = "destructible-wall"
    INDESTRUCTIBLE_WALL = "indestructible-wall"

    def __init__(self, window):
        super().__init__(window)

    def entity_added(self, entity, view_qualifier):
        if view_qualifier == self.BACKGROUND:
            self.sprite_factory.color(entity, self.layout, colors.GRAY)

    def entity_changed(self, entity, view_qualifier, key, value):
        pass
