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
        sdl2.ext.fill(self.surface, sdl2.ext.Color(255, 0, 0))
        super().render(sprites)


class GameRendererSystem(StateBasedRendererSystem):
    def __init__(self, window, state):
        super().__init__(window, state)
        self.block_size = None


    def render(self, sprites=[], x=None, y=None):
        sprites = []
        if self.state.game_board is not None:
            game_board_size =  (len(self.state.game_board), len(self.state.game_board[0]))
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
            text = self.factory.from_text(text="Press enter to start", fontmanager=self.fontmanager)
            text.position = (0, int(client_configuration.screen_size[1]/2))
            sprites.append(text)
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super().render(sprites)

    def transform_sprite(self, entity):
        if isinstance(entity, PlayerEntity):
            sdl2.ext.fill(entity.sprite, (0, 0, 255))
        if isinstance(entity, DestructibleWallEntity):
            sdl2.ext.fill(entity.sprite, (128, 128, 128))
        if isinstance(entity, IndestructibleWallEntity):
            sdl2.ext.fill(entity.sprite, (255, 255, 255))

