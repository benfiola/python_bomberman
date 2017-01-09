from client.controllers import *


class SinglePlayerOptionsController(Controller):
    def __init__(self, client):
        super().__init__(client)

    def set_up(self):
        super().set_up()
        self.layout.finalize(self.window_size)

        background_entity = entities.ColorEntity(self, graphics.Colors.GRAY)
        self.sprite_factory.color(background_entity, self.layout)

        title_entity = entities.LabelEntity(self, "Single-Player Options", graphics.Colors.WHITE)
        self.sprite_factory.text(title_entity, self.layout.container("title"))

        self.world.add_system(systems.SoftwareRenderer(self.client.window))

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            from client.controllers.main_menu import MainMenuController
            self.client.add_event(events.ControllerTransition(MainMenuController))
