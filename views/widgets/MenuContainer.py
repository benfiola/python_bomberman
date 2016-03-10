import pygame

from views.Colors import Colors
from views.animations.Animations import SlideAnimationData
from views.widgets.MyLayeredUpdates import MyLayeredUpdates
from views.widgets.MySprite import MySprite
from views.widgets.SelectionWidget import SelectionWidget


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




