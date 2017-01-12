import sdl2.ext
import client.platform_utils as platform_utils


class BaseSpriteFactory(sdl2.ext.SpriteFactory):
    def __init__(self, sprite_type=sdl2.ext.SOFTWARE, **kwargs):
        super().__init__(sprite_type, **kwargs)
        font_path = platform_utils.Platform.get_platform().get_font_path("Arial")
        self.font_manager = sdl2.ext.FontManager(font_path=font_path)

    def color(self, entity, layout, color, **kwargs):
        sprite = super().from_color(color, layout.absolute_size, **kwargs)
        sprite.position = layout.absolute_location
        sprite.depth = layout.depth
        entity._sdl2_entity.sprite = sprite
        return sprite

    def text(self, entity, text, layout, color, center_x=True, center_y=True, **kwargs):
        sprite = super().from_text(text, color=color, fontmanager=self.font_manager, **kwargs)

        container_size = layout.absolute_size
        offset = (int((container_size[0]/2)-(sprite.size[0]/2)), int((container_size[1]/2)-(sprite.size[1]/2)))

        position = layout.absolute_location
        if center_x:
            position = (position[0]+offset[0], position[1])
        if center_y:
            position = (position[0], position[1]+offset[1])
        sprite.position = position
        sprite.depth = layout.depth
        entity._sdl2_entity.sprite = sprite
        return sprite
