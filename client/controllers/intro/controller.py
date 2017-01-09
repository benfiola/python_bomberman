from client.controllers.common import *


class IntroController(Controller):
    def __init__(self, client):
        super().__init__(client)

    def set_up(self):
        super().set_up()
        background_entity = entities.ColorEntity(self, graphics.Colors.BLUE)
        self.sprite_factory.color(background_entity, self.layout)
        title_entity = entities.LabelEntity(self, "Bomberman", graphics.Colors.WHITE)
        self.sprite_factory.text(title_entity, self.layout.container("title"))
        enter_entity = entities.LabelEntity(self, "Press ENTER to continue.", graphics.Colors.WHITE)
        self.sprite_factory.text(enter_entity, self.layout.container("enter-message"))
        esc_entity = entities.LabelEntity(self, "Press ESC to exit.", graphics.Colors.WHITE)
        self.sprite_factory.text(esc_entity, self.layout.tagged_containers["esc-message"])

        self.world.add_system(systems.SoftwareRenderer(self.client.window))

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            self.client.add_event(events.Quit())
        if key_code == events.KeyInputEvent.RETURN:
            from client.controllers.main_menu import MainMenuController
            self.client.add_event(events.ControllerTransition(MainMenuController))