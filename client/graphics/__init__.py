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
                for entity_list in row:
                    for entity in entity_list:
                        if entity.sprite is None:
                            self.create_sprite(entity)
                        if self.update_needed(entity):
                            old_entities = self.get_entities_at_position(entity.sprite.position)
                            base_sprite = self.create_sprite(None)
                            self.update_sprite_position(base_sprite, position=entity.sprite.position)
                            sprites.append(base_sprite)
                            for old_entity in old_entities:
                                self.create_sprite(old_entity)
                                self.update_sprite_position(old_entity.sprite, entity=old_entity)
                                sprites.append(old_entity.sprite)
                            self.update_sprite_position(entity.sprite, entity=entity)
                            sprites.append(entity.sprite)
        super().render(sprites)

    def create_sprite(self, entity):
        # create a new sprite, give it a bogus location so that it gets properly updated
        sprite = self.factory.create_sprite(size=self.block_size, bpp=32)
        sprite.position = (-255, -255)
        if entity is None:
            sdl2.ext.fill(sprite, (0, 0, 0))
            sprite.depth = 0
        else:
            entity.sprite = sprite
            if isinstance(entity, PlayerEntity):
                sdl2.ext.fill(sprite, (0, 0, 255))
                sprite.depth = 3
            if isinstance(entity, DestructibleWallEntity):
                sdl2.ext.fill(sprite, (128, 128, 128))
                sprite.depth = 1
            if isinstance(entity, IndestructibleWallEntity):
                sdl2.ext.fill(sprite, (255, 255, 255))
                sprite.depth = 1
            if isinstance(entity, BombEntity):
                sdl2.ext.fill(sprite, (0, 255, 0))
                sprite.depth = 2
            if isinstance(entity, FireEntity):
                sdl2.ext.fill(sprite, (255, 0, 0))
                sprite.depth = 4
        return sprite

    def get_entities_at_position(self, pos):
        index = (int(pos[0] / self.block_size[0]), int(pos[1] / self.block_size[1]))
        if index[0] >= 0 or index[1] >= 0:
            return self.state.game_board[index[0]][index[1]]
        return []

    def update_sprite_position(self, sprite, entity=None, position=None):
        if entity is not None:
            sprite.position = (entity.position[0] * self.block_size[0], entity.position[1] * self.block_size[1])
        if position is not None:
            sprite.position = (position[0], position[1])

    def update_needed(self, entity):
        old_pos = entity.sprite.position
        new_pos = (entity.position[0] * self.block_size[0], entity.position[1] * self.block_size[1])
        return old_pos[0] != new_pos[0] or old_pos[1] != new_pos[1]
