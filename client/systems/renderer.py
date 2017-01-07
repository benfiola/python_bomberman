from client.graphics.colors import Colors
import sdl2.ext


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super().__init__(window)

    def render(self, components):
        super().render(components)
