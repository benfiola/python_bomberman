import sdl2.ext

from client.view_states import *
from common.configuration import client_configuration

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


class MenuRendererSystem(StateBasedRendererSystem):
    def __init__(self, window, state):
        super().__init__(window, state)

    def render(self, sprites=[], x=None, y=None):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(255, 0, 0))
        super().render(sprites)


class GameRendererSystem(StateBasedRendererSystem):
    def __init__(self, window, state):
        super().__init__(window, state)

    def render(self, sprites=[], x=None, y=None):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 255, 0))
        super().render(sprites)