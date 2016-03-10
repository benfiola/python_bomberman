import pygame

class MyLayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super(MyLayeredUpdates, self).__init__()

    def add_sprite_to_layer(self, sprite, layer):
        kwargs = {"layer":layer}
        self.add(sprite, **kwargs)

    def position(self, pos):
        for layer_index in self.layers():
            for sprite in self.get_sprites_from_layer(layer_index):
                topleft = sprite.rect.topleft
                new_pos = (pos[0]+topleft[0], pos[1]+topleft[1])
                sprite.rect = pygame.Rect(new_pos, sprite.rect.size)