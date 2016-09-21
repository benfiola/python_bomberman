import sdl2.ext
from common.logging import get_logger
from client import custom_events
from common.entities import *
from common.configuration import get_default_game_configuration
from common.messaging import messages
from host import get_default_host_config


class ViewState(object):
    def __init__(self, client, substate_cls):
        self.client = client
        self.logger = get_logger(self)
        self.substate = substate_cls(self)

    def clean_up(self):
        pass

    def change_substate(self, substate_cls):
        self.substate = substate_cls(self)

    def process_event(self, event):
        if isinstance(event, custom_events.CustomEvent):
            self.handle_custom_event(event)
        else:
            self.handle_sdl2_event(event)

    def handle_custom_event(self, event):
        self.substate.handle_custom_event(event)

    def handle_sdl2_event(self, event):
        self.substate.handle_sdl2_event(event)


class GameState(ViewState):
    def __init__(self, client):
        super().__init__(client, PreGameState)
        self.game_board = None


class ViewSubState(object):
    def __init__(self, state):
        super().__init__()
        self.client = state.client
        self.state = state

    def handle_custom_event(self, event):
        pass

    def handle_sdl2_event(self, event):
        pass


class MenuSubState(ViewSubState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_RETURN:
                self.client.push_custom_event(custom_events.ViewStateChange(GameState))
            elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                self.client.push_custom_event(custom_events.QuitEvent())


class GameSubState(ViewSubState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                self.client.push_custom_event(custom_events.DisconnectFromHost())
                self.client.push_custom_event(custom_events.ViewStateChange(MenuState))


class PreGameState(GameSubState):
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
                self.state.change_substate(HostStartedGameState)
            if event.key.keysym.sym == sdl2.SDLK_w:
                host_config = get_default_host_config()
                self.client.push_custom_event(custom_events.ConnectToHost(host_config))
                self.client.push_custom_event(custom_events.SendMessage(messages.AssignPlayerEntityRequest()))
                self.state.change_substate(ClientStartedGameState)


class HostStartedGameState(GameSubState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)
        if isinstance(event, custom_events.InitializeGameData):
            self.state.game_board = event.game_board
            self.state.change_substate(InGameState)

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_e:
                self.client.push_custom_event(custom_events.SendMessage(messages.StartGameRequest()))


class ClientStartedGameState(GameSubState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)
        if isinstance(event, custom_events.InitializeGameData):
            self.state.game_board = event.game_board
            self.state.change_substate(InGameState)

    def handle_sdl2_event(self, event):
        super().handle_sdl2_event(event)


class InGameState(GameSubState):
    def __init__(self, *args):
        super().__init__(*args)

    def handle_custom_event(self, event):
        super().handle_custom_event(event)
        if isinstance(event, custom_events.UpdateGameData):
            for key in event.update_data:
                if key == "entity_remove":
                    for entity in event.update_data[key]:
                        curr_entities = self.state.game_board[entity.position[0]][entity.position[1]]
                        for curr_entity in list(curr_entities):
                            if isinstance(curr_entity, entity.__class__):
                                curr_entities.remove(curr_entity)
                                break
                if key == "entity_add":
                    for entity in event.update_data[key]:
                        self.state.game_board[entity.position[0]][entity.position[1]].append(entity)
                if key == "entity_move":
                    (old_pos, new_pos) = event.update_data[key]
                    old_entities = self.state.game_board[old_pos[0]][old_pos[1]]
                    new_entities = self.state.game_board[new_pos[0]][new_pos[1]]
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


class MenuState(ViewState):
    def __init__(self, client):
        super().__init__(client, MenuSubState)
