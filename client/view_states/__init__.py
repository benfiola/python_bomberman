import sdl2.ext
from common.logging import get_logger
from client import custom_events
from common.configuration import get_default_game_configuration
from common.messaging import messages
from host import get_default_host_config


class ViewState(object):
    def __init__(self, client):
        self.client = client
        self.logger = get_logger(self)

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
        self.game_board = None

    def handle_custom_event(self, event):
        if isinstance(event, custom_events.InitializeGameData):
            self.game_board = event.game_board

    def handle_sdl2_event(self, event):
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                self.client.push_custom_event(custom_events.DisconnectFromHost())
                self.client.push_custom_event(custom_events.ViewStateChange(MenuState))
            if event.key.keysym.sym == sdl2.SDLK_q:
                host_config = get_default_host_config()
                self.client.push_custom_event(custom_events.CreateHost(host_config))
                self.client.push_custom_event(custom_events.ConnectToHost(host_config))
                self.client.push_custom_event(
                    custom_events.SendMessage(messages.InitializeGameRequest(get_default_game_configuration())))
            elif event.key.keysym.sym == sdl2.SDLK_w:
                host_config = get_default_host_config()
                self.client.push_custom_event(custom_events.ConnectToHost(host_config))
            elif event.key.keysym.sym == sdl2.SDLK_e:
                self.client.push_custom_event(custom_events.SendMessage(messages.AssignPlayerEntityRequest()))
            elif event.key.keysym.sym == sdl2.SDLK_r:
                self.client.push_custom_event(custom_events.SendMessage(messages.StartGameRequest()))
            elif event.key.keysym.sym == sdl2.SDLK_UP:
                self.client.push_custom_event(custom_events.SendMessage(messages.MoveEntityRequest((0, 1))))
            elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                self.client.push_custom_event(custom_events.SendMessage(messages.MoveEntityRequest((0, -1))))
            elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                self.client.push_custom_event(custom_events.SendMessage(messages.MoveEntityRequest((-1, 0))))
            elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                self.client.push_custom_event(custom_events.SendMessage(messages.MoveEntityRequest((1, 0))))


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

