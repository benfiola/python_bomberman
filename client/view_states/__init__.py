import sdl2.ext
from common.app_logging import get_logger
from client import custom_events
from common.entities import *
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


class MenuState(ViewState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_RETURN:
                self.client.push_custom_event(custom_events.ViewStateChange(PreGameState(self.client)))
            elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                self.client.push_custom_event(custom_events.QuitEvent())


class GameState(ViewState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)


class PreGameState(GameState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_q:
                host_config = get_default_host_config()
                self.client.push_custom_event(custom_events.CreateHost(host_config))
                self.client.push_custom_event(custom_events.ConnectToHost(host_config))
                self.client.push_custom_event(
                    custom_events.SendMessage(messages.InitializeGameRequest(get_default_game_configuration())))
                self.client.push_custom_event(custom_events.SendMessage(messages.AssignPlayerEntityRequest()))
                self.client.push_custom_event(custom_events.ViewStateChange(HostStartedGameState(self.client)))
            if event.key.keysym.sym == sdl2.SDLK_w:
                host_config = get_default_host_config()
                self.client.push_custom_event(custom_events.ConnectToHost(host_config))
                self.client.push_custom_event(custom_events.SendMessage(messages.AssignPlayerEntityRequest()))
                self.client.push_custom_event(custom_events.ViewStateChange(ClientStartedGameState(self.client)))


class HostStartedGameState(GameState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)
        if isinstance(event, custom_events.InitializeGameData):
            self.client.push_custom_event(custom_events.ViewStateChange(InGameState(self.client, event.game_board)))

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_e:
                self.client.push_custom_event(custom_events.SendMessage(messages.StartGameRequest()))


class ClientStartedGameState(GameState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)
        if isinstance(event, custom_events.InitializeGameData):
            self.client.push_custom_event(custom_events.ViewStateChange(InGameState(self.client, event.game_board)))

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)


class InGameState(GameState):
    def __init__(self, *args):
        self.game_board = args[1]
        super().__init__(args[0])

    def handle_custom_event(self, event):
        super().handle_custom_event(event)
        if isinstance(event, custom_events.UpdateGameData):
            for key in event.update_data:
                if key == "entity_remove":
                    for entity in event.update_data[key]:
                        curr_entities = self.game_board[entity.position[0]][entity.position[1]]
                        for curr_entity in list(curr_entities):
                            if isinstance(curr_entity, entity.__class__):
                                curr_entities.remove(curr_entity)
                                break
                if key == "entity_add":
                    for entity in event.update_data[key]:
                        self.game_board[entity.position[0]][entity.position[1]].append(entity)
                if key == "entity_move":
                    (old_pos, new_pos) = event.update_data[key]
                    old_entities = self.game_board[old_pos[0]][old_pos[1]]
                    new_entities = self.game_board[new_pos[0]][new_pos[1]]
                    player_entity = None
                    for old_entity in list(old_entities):
                        if isinstance(old_entity, PlayerEntity):
                            player_entity = old_entity
                            old_entities.remove(old_entity)
                            break
                    if player_entity is None:
                        raise Exception("What the heck.")
                    player_entity.position = new_pos
                    new_entities.append(player_entity)

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_UP:
                self.client.push_custom_event(custom_events.SendMessage(messages.MoveEntityRequest((0, -1))))
            elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                self.client.push_custom_event(custom_events.SendMessage(messages.MoveEntityRequest((0, 1))))
            elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                self.client.push_custom_event(custom_events.SendMessage(messages.MoveEntityRequest((-1, 0))))
            elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                self.client.push_custom_event(custom_events.SendMessage(messages.MoveEntityRequest((1, 0))))
            elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                self.client.push_custom_event(custom_events.SendMessage(messages.AddBombRequest()))
