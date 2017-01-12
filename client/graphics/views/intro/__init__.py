from client.graphics.views import *


class IntroView(View):
    def __init__(self, window):
        super().__init__(window)

    def prepare_layout(self):
        pass

    def on_entity_add(self, entity, view_qualifier):
        if view_qualifier == "background":
            self.sprite_factory.color(entity, self.layout, colors.BLACK)
        if view_qualifier == "title":
            layout = self.layout.container("title")
            self.sprite_factory.text(entity, "Bomberman", layout, colors.WHITE)
        if view_qualifier == "enter-message":
            layout = self.layout.container("enter-message")
            self.sprite_factory.text(entity, "Press ENTER to start", layout, colors.WHITE)
        if view_qualifier == "esc-message":
            layout = self.layout.container("esc-message")
            self.sprite_factory.text(entity, "Press ESC to exit", layout, colors.WHITE)

    def on_entity_change(self, entity, key, value):
        pass
