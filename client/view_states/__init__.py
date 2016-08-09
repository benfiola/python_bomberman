import sdl2.ext
from client import custom_events
from common.configuration import get_default_game_configuration
from common.messaging import messages
from host import get_default_host_config


class ViewState(object):
    def __init__(self, client):
        self.client = client

    def clean_up(self):
        pass

    def process_event(self, event):
        if isinstance(event, custom_events.CustomEvent):
            self.handle_custom_event(event)
        else:
            self.handle_sdl2_event(event)

    def handle_custom_event(self, event):
        pass

    def handle_sdl2_event(self, event):
        pass


class GameState(ViewState):
    def __init__(self, client):
        super().__init__(client)
        host_config = get_default_host_config()
        self.client.push_custom_event(custom_events.CreateHost(host_config))
        self.client.push_custom_event(custom_events.ConnectToHost(host_config))
        self.client.push_custom_event(custom_events.SendMessage(messages.InitializeGameMessage(get_default_game_configuration())))
        self.client.push_custom_event(custom_events.SendMessage(messages.StartGameMessage()))

    def handle_custom_event(self, event):
        pass

    def handle_sdl2_event(self, event):
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                self.client.push_custom_event(custom_events.DisconnectFromHost())
                self.client.push_custom_event(custom_events.ViewStateChange(MenuState))
            elif event.key.keysym.sym == sdl2.SDLK_RETURN:
                pass


class MenuState(ViewState):
    def __init__(self, client):
        super().__init__(client)

    def handle_custom_event(self, event):
        pass

    def handle_sdl2_event(self, event):
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_RETURN:
                self.client.push_custom_event(custom_events.ViewStateChange(GameState))
            elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                self.client.push_custom_event(custom_events.QuitEvent())

    def clean_up(self):
        pass

