from common import logging
import client.events as events


class Controller(object):
    def __init__(self, client):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = client

    def _key_down(self, event):
        self.on_key_down(event.key_code)

    def _key_up(self, event):
        self.on_key_down(event.key_code)

    def set_up(self):
        self.client.register_event_handler(events.KeyInputDown, self._key_down)
        self.client.register_event_handler(events.KeyInputDown, self._key_up)

    def tear_down(self):
        self.client.remove_event_handlers(self)

    def on_key_down(self, key_code):
        pass

    def on_key_up(self, key_code):
        pass


class IntroController(Controller):
    def __init__(self, client):
        super().__init__(client)

    def set_up(self):
        super().set_up()

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            self.client.add_event(events.Quit())
        if key_code == events.KeyInputEvent.RETURN:
            self.client.add_event(events.ControllerTransition(MainMenuController))


class MainMenuController(Controller):
    def __init__(self, client):
        super().__init__(client)

    def set_up(self):
        super().set_up()
        self.client.register_event_handler(events.KeyInputDown, self.on_key_down)

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            self.client.add_event(events.ControllerTransition(IntroController))
