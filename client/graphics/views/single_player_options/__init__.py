from client.graphics.views import *


class SinglePlayerOptionsView(View):
    BACKGROUND = "background"
    TITLE = "title"

    def __init__(self, window):
        super().__init__(window)

    def entity_added(self, entity, view_qualifier):
        if view_qualifier == self.BACKGROUND:
            self.sprite_factory.color(entity, self.layout, colors.PURPLE)
        if view_qualifier == self.TITLE:
            self.sprite_factory.text(entity, "Single-player Options", self.layout.container(tag="title"), colors.WHITE)

    def entity_changed(self, entity, view_qualifier, key, value):
        pass
