from client.graphics.colors import Colors
import sdl2.ext


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window, bg_color=Colors.BLACK):
        super().__init__(window)
        self.bg_color = bg_color

    def render(self, components):
        sdl2.ext.fill(self.surface, self.bg_color)
        super().render(components)