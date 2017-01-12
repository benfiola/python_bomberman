from client.controllers import *
import client.graphics.views.intro as view


class IntroController(Controller):
    def __init__(self, client):
        super().__init__(client, view.IntroView)

    def set_up(self):
        entities.ClientEntity(self, view_qualifier="background")
        entities.ClientEntity(self, view_qualifier="title")
        entities.ClientEntity(self, view_qualifier="enter-message")
        entities.ClientEntity(self, view_qualifier="esc-message")

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            self.client.add_event(events.Quit())
        if key_code == events.KeyInputEvent.RETURN:
            from client.controllers.main_menu import MainMenuController
            self.client.add_event(events.ControllerTransition(MainMenuController))