from client.graphics.views import *


class MultiPlayerOptionsView(View):
    BACKGROUND = "background"
    TITLE = "title"

    def __init__(self, window):
        super().__init__(window)

    def entity_added(self, entity, view_qualifier):
        if view_qualifier == self.BACKGROUND:
            self.sprite_factory.color(entity, self.layout, colors.LIGHT_BLUE)
        if view_qualifier == self.TITLE:
            self.sprite_factory.text(entity, "Multi-player Options", self.layout.container(tag="title"), colors.WHITE)

    def entity_changed(self, entity, view_qualifier, key, value):
        pass
