import pygame
from views.widgets.MyLayeredUpdates import MyLayeredUpdates


class MySprite(pygame.sprite.Sprite):
    def __init__(self):
        super(MySprite, self).__init__()
        self.animation_data = None

    def update(self):
        if self.animation_data is not None:
            self.animation_data.function(self)

    def to_layer_group(self, position=(0,0)):
        to_return = MyLayeredUpdates()
        to_return.add_sprite_to_layer(self, 0)
        to_return.position(position)
        return to_return
