from client.controllers import *
import client.graphics.views.single_player as view


class SinglePlayerController(Controller):
    def __init__(self, client):
        super().__init__(client, view.SinglePlayerView)

    def set_up(self):
        entities.ClientEntity(self, view_qualifier="background")
        entities.ClientEntity(self, view_qualifier="title")

    def tear_down(self):
        self.client.add_event(events.StopMessageBus())

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            from client.controllers.main_menu import MainMenuController
            self.client.add_event(events.ControllerTransition(MainMenuController))

