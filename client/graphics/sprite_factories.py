import sdl2.ext
import client.platform_utils as platform_utils


class BaseSpriteFactory(sdl2.ext.SpriteFactory):
    def __init__(self, sprite_type=sdl2.ext.SOFTWARE, **kwargs):
        super().__init__(sprite_type, **kwargs)
        font_path = platform_utils.Platform.get_platform().get_font_path("Arial")
        self.font_manager = sdl2.ext.FontManager(font_path=font_path)

    def color(self, color, layout, **kwargs):
        sprite = super().from_color(color, layout.absolute_size, **kwargs)
        sprite.position = layout.absolute_location
        sprite.depth = layout.depth
        return sprite

    def text(self, text, layout, **kwargs):
        sprite = super().from_text(text, fontmanager=self.font_manager, **kwargs)
        sprite.position = layout.absolute_location
        sprite.depth = layout.depth
        return sprite
