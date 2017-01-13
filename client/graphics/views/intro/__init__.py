from client.graphics.views import *


class IntroView(View):
    BACKGROUND = "background"
    TITLE = "title"
    ESC_MESSAGE = "esc-message"
    ENTER_MESSAGE = "enter-message"

    def __init__(self, window):
        super().__init__(window)

    def entity_added(self, entity, view_qualifier):
        if view_qualifier == self.BACKGROUND:
            self.sprite_factory.color(entity, self.layout, colors.BLACK)
        if view_qualifier == self.TITLE:
            layout = self.layout.container(tag="title")
            self.sprite_factory.text(entity, "Bomberman", layout, colors.WHITE)
        if view_qualifier == self.ENTER_MESSAGE:
            layout = self.layout.container(tag="enter-message")
            self.sprite_factory.text(entity, "Press ENTER to start", layout, colors.WHITE)
        if view_qualifier == self.ESC_MESSAGE:
            layout = self.layout.container(tag="esc-message")
            self.sprite_factory.text(entity, "Press ESC to exit", layout, colors.WHITE)
