import sdl2.ext

from client.view_states import *
from common.configuration import client_configuration
from common.entities import *
from client.platform import get_font_path

class GameWindow(sdl2.ext.Window):
    def __init__(self, state):
        super().__init__(client_configuration.game_name, size=client_configuration.screen_size)
        self.renderer = None
        self.change_renderer(state)

    def change_renderer(self, state):
        if isinstance(state, MenuState):
            self.renderer = MenuRendererSystem(self, state)
        if isinstance(state, GameState):
            self.renderer = GameRendererSystem(self, state)

    def refresh(self):
        self.renderer.render()
        super().refresh()


class StateBasedRendererSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window, state):
        super().__init__(window=window)
        self.state = state
        self.factory = sdl2.ext.SpriteFactory(sprite_type=sdl2.ext.SOFTWARE)
        self.fontmanager = sdl2.ext.FontManager(font_path=get_font_path("Arial"), size=16, color=(255, 255, 255))


class MenuRendererSystem(StateBasedRendererSystem):
    def __init__(self, window, state):
        super().__init__(window, state)

    def render(self, sprites=[], x=None, y=None):
        sprites = []
        sdl2.ext.fill(self.surface, sdl2.ext.Color(255, 0, 0))
        if isinstance(self.state.substate, MenuSubState):
            text = self.factory.from_text(text="Press enter to start", fontmanager=self.fontmanager)
            text.position = (0, (int(client_configuration.screen_size[1] / 2)) - 16)
            sprites.append(text)
            text = self.factory.from_text(text="Press escape to quit", fontmanager=self.fontmanager)
            text.position = (0, int(client_configuration.screen_size[1]/2))
            sprites.append(text)
        super().render(sprites)


class GameRendererSystem(StateBasedRendererSystem):
    def __init__(self, window, state):
        super().__init__(window, state)
        self.block_size = None
        self.initialize_board = True

    def render(self, sprites=[], x=None, y=None):
        sprites = []
        if isinstance(self.state.substate, PreGameState):
            sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
            text = self.factory.from_text(text="Press q to host a game", fontmanager=self.fontmanager)
            text.position = (0, (int(client_configuration.screen_size[1] / 2)) - 16)
            sprites.append(text)
            text = self.factory.from_text(text="Press w to connect to a game", fontmanager=self.fontmanager)
            text.position = (0, int(client_configuration.screen_size[1] / 2))
            sprites.append(text)
        if isinstance(self.state.substate, HostStartedGameState):
            sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
            text = self.factory.from_text(text="Press e to start the game", fontmanager=self.fontmanager)
            text.position = (0, int(client_configuration.screen_size[1] / 2))
            sprites.append(text)
        if isinstance(self.state.substate, ClientStartedGameState):
            sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
            text = self.factory.from_text(text="Waiting for host to start game", fontmanager=self.fontmanager)
            text.position = (0, int(client_configuration.screen_size[1] / 2))
            sprites.append(text)
        if isinstance(self.state.substate, InGameState):
            # on first draw clear the screen - we should do better than this check though
            if self.block_size is None:
                sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
            game_board_size = (len(self.state.game_board), len(self.state.game_board[0]))
            window_size = client_configuration.screen_size
            self.block_size = (int(window_size[0]/game_board_size[0]), int(window_size[1]/game_board_size[1]))
            for row in self.state.game_board:
                for entity in row:
                    if entity is not None:
                        if entity.sprite is None:
                            entity.sprite = self.factory.create_sprite(size=self.block_size, bpp=32)
                            self.transform_sprite(entity)
                            entity.sprite.position = (entity.position[0] * self.block_size[0], entity.position[1] * self.block_size[1])
                            sprites.append(entity.sprite)
                        else:
                            old_pos = entity.sprite.position
                            new_pos = (entity.position[0] * self.block_size[0], entity.position[1] * self.block_size[1])
                            if old_pos[0] != new_pos[0] or old_pos[1] != new_pos[1]:
                                old_index = (int(old_pos[0]/self.block_size[0]), int(old_pos[1]/self.block_size[1]))
                                old_entity = self.state.game_board[old_index[0]][old_index[1]]
                                old_sprite = None
                                if old_entity is not None:
                                    old_sprite = old_entity.sprite
                                else:
                                    old_sprite = self.factory.create_sprite(size=self.block_size, bpp=32)
                                    sdl2.ext.fill(old_sprite, (0, 0, 0))
                                old_sprite.position = old_pos
                                sprites.append(old_sprite)
                                entity.sprite.position = new_pos
                                sprites.append(entity.sprite)
        super().render(sprites)

    def transform_sprite(self, entity):
        if isinstance(entity, PlayerEntity):
            sdl2.ext.fill(entity.sprite, (0, 0, 255))
        if isinstance(entity, DestructibleWallEntity):
            sdl2.ext.fill(entity.sprite, (128, 128, 128))
        if isinstance(entity, IndestructibleWallEntity):
            sdl2.ext.fill(entity.sprite, (255, 255, 255))

