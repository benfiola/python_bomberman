import pygame
from animations import SlideAnimationData
from colors import Colors

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


class SelectionWidget(MySprite):
    def __init__(self, size, color):
        super(SelectionWidget, self).__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by set
        self.rect = self.image.get_rect()


class MenuContainer(MySprite):
    def __init__(self, widgets, color):
        super(MenuContainer, self).__init__()
        self.options = []
        self.selection = None

        size = (0,0)
        # figure out container size
        for widget in widgets:
            self.options.append(widget)
            if size[0] < widget.rect.size[0]:
                size = (widget.rect.size[0], size[1])
            size = (size[0], size[1] + widget.rect.size[1])

        # create the sprite
        self.image = pygame.Surface(size)
        self.image.fill(color)

        # now adjust the widget rects for each widget
        widget_y = 0
        for widget in widgets:
            widget_size = widget.rect.size
            widget.rect = pygame.Rect((0, widget_y), (size[0],widget_size[1]))
            widget_y += widget_size[1]

        selection_size = (size[0],size[1]/len(self.options))
        self.selection = SelectionWidget(selection_size, Colors.RED)

        self.rect = self.image.get_rect()

    def option_change(self, index):
            target = self.options[index]
            self.selection.animation_data = SlideAnimationData(100.0, self.selection.rect.topleft, target.rect.topleft)

    def to_layer_group(self):
        to_return = MyLayeredUpdates()
        to_return.add_sprite_to_layer(self, 0)
        to_return.add_sprite_to_layer(self.selection, 1)
        for widget in self.options:
            to_return.add_sprite_to_layer(widget, 2)
        return to_return


class LabelWidget(MySprite):
    def __init__(self, text, font_size, color, padding=(0,0,0,0)):
        super(LabelWidget, self).__init__()

        font = pygame.font.Font(None, font_size)
        font_surface = font.render(text, True, color)

        padding_top = padding[0]
        padding_right = padding[1]
        padding_bottom = padding[2]
        padding_left = padding[3]

        font_sprite_size = font_surface.get_size()
        image_size = (font_sprite_size[0]+padding_left+padding_right, font_sprite_size[1]+padding_top+padding_bottom)
        self.image = pygame.Surface(image_size, pygame.SRCALPHA, 32)
        self.image.blit(font_surface, (padding_left,padding_top))

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
