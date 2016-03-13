from time import time

from pygame import display
from pygame import Surface
from time import time
from colors import *
from widgets import *
from animations import *

class AbstractView(object):
    VIEW_TRANSITION_TIME = 100

    def __init__(self, backing_model, bg_color=Colors.BLACK):
        self.surface = None
        self.backing_model = backing_model
        self.layer_groups = []
        self.bg_color = bg_color

    # initialize_surface is called prior to a view transition
    # it basically prepares a screen
    def initialize_surface(self, model):
        curr_surface = display.get_surface()
        self.surface = Surface(curr_surface.get_size())
        self.surface.fill(self.bg_color)

    # called on every cycle to update the current view
    def update(self):
        rects = []
        for layer_group in self.layer_groups:
            for layer_index in layer_group.layers():
                for sprite in layer_group.get_sprites_from_layer(layer_index):
                    sprite.update()
            rects.extend(layer_group.draw(display.get_surface()))
        display.update(rects)

    # prior to animating away from this view, we save what we have to our surface.
    # when we navigate back to this screen, we just need to copy this to the main
    # surface and we're good to go again.
    def save(self):
        self.surface = display.get_surface().copy()

    # this is a weird edge case - normally you animate within a single view
    # but what if you're animating between views during a controller transition?
    # i decided to make this animation blocking, and it basically serves to perform
    # a better-than-nothing sliding animation between two screens.
    def slide_right(self):
        start_time = time() * 1000
        duration = (time()*1000) - start_time
        width = display.get_surface().get_size()[0]
        old_surface = display.get_surface().copy()

        while duration < AbstractView.VIEW_TRANSITION_TIME:
            progress = duration / AbstractView.VIEW_TRANSITION_TIME
            x_offset = (-width)+(width*progress)
            old_surface_x_offset = x_offset + width
            display.get_surface().blit(old_surface, (old_surface_x_offset, 0))
            display.get_surface().blit(self.surface, (x_offset, 0))
            display.flip()
            duration = (time.time()*1000) - start_time
        display.get_surface().blit(self.surface, (0, 0))
        display.flip()

    # same as above, but in opposite direction.  could generalize this, am lazy.
    def slide_left(self):
        start_time = time.time() * 1000
        duration = (time.time()*1000) - start_time
        width = display.get_surface().get_size()[0]
        old_surface = display.get_surface().copy()

        while duration < AbstractView.VIEW_TRANSITION_TIME:
            progress = duration / AbstractView.VIEW_TRANSITION_TIME
            x_offset = width-(width*progress)
            old_surface_x_offset = x_offset - width
            display.get_surface().blit(old_surface, (old_surface_x_offset, 0))
            display.get_surface().blit(self.surface, (x_offset, 0))
            display.flip()
            duration = (time.time()*1000) - start_time
        display.get_surface().blit(self.surface, (0, 0))
        display.flip()

class MainMenuView(AbstractView):
    def __init__(self, backing_model):
        super(MainMenuView, self).__init__(backing_model=backing_model, bg_color=Colors.BLUE)
        self.title = None
        self.container = None
        self.selection = None

    def initialize_surface(self, model):
        super(MainMenuView, self).initialize_surface(model)

        # prepare the title
        self.title = LabelWidget("Main Menu", 36, Colors.WHITE)
        surface_center = self.surface.get_rect().center
        title_center = self.title.rect.center
        title_position = (surface_center[0]-title_center[0], 0)

        # prepare the menu options container
        font_size = 24
        option_widgets = []
        for option in model.options:
            curr_widget = LabelWidget(option.text, font_size, Colors.WHITE, padding=(12,12,12,12))
            option_widgets.append(curr_widget)

        self.container = MenuContainer(option_widgets, Colors.BLACK)
        container_center = self.container.rect.center
        container_position = (surface_center[0]-container_center[0], surface_center[1])

        title_layer_group = self.title.to_layer_group()
        container_layer_group = self.container.to_layer_group()
        title_layer_group.position(title_position)
        container_layer_group.position(container_position)
        title_layer_group.draw(self.surface)
        container_layer_group.draw(self.surface)

        self.layer_groups.append(self.title.to_layer_group())
        self.layer_groups.append(self.container.to_layer_group())

    def option_change(self, model):
        self.container.option_change(model.selection)

class TitleScreenView(AbstractView):
    def __init__(self, backing_model):
        super(TitleScreenView, self).__init__(backing_model=backing_model, bg_color=Colors.RED)
        self.title = None
        self.subtext = None

    def initialize_surface(self, model):
        super(TitleScreenView, self).initialize_surface(model)
        self.title = LabelWidget("Bombenman", 72, Colors.WHITE)
        self.subtext = LabelWidget("Press enter", 36, Colors.WHITE)

        surface_center = self.surface.get_rect().center
        title_center = self.title.rect.center
        subtext_center = self.subtext.rect.center

        title_position = (surface_center[0]-title_center[0],0)
        subtext_position = (surface_center[0]-subtext_center[0], surface_center[1] + (surface_center[1]/2))

        title_layer_group = self.title.to_layer_group(title_position)
        subtext_layer_group = self.subtext.to_layer_group(subtext_position)
        self.layer_groups.extend([title_layer_group, subtext_layer_group])

class MultiplayerView(AbstractView):
    def __init__(self, backing_model):
        super(MultiplayerView, self).__init__(backing_model, bg_color=Colors.WHITE)

class MultiplayerOptionsView(AbstractView):
    def __init__(self, backing_model):
        super(MultiplayerOptionsView, self).__init__(backing_model=backing_model, bg_color=Colors.GRAY)

    def initialize_surface(self, model):
        super(MultiplayerOptionsView, self).initialize_surface(model)
        title_widget = LabelWidget("Multiplayer Options", 36, Colors.BLACK)

        surface_center = self.surface.get_rect().center
        title_center = title_widget.rect.center

        self.surface.blit(title_widget.image, (surface_center[0]-title_center[0], 0))

class SinglePlayerOptionsView(AbstractView):
    def __init__(self, backing_model):
        super(SinglePlayerOptionsView, self).__init__(backing_model=backing_model, bg_color=Colors.WHITE)

    def initialize_surface(self, model):
        super(SinglePlayerOptionsView, self).initialize_surface(model)
        title_widget = LabelWidget("Single Player Options", 36, Colors.BLACK)

        surface_center = self.surface.get_rect().center
        title_center = title_widget.rect.center

        self.surface.blit(title_widget.image, (surface_center[0]-title_center[0], 0))

class SinglePlayerView(AbstractView):
    def __init__(self, backing_model):
        super(OptionsView, self).__init__(backing_model=backing_model, bg_color=Colors.RED)

    def initialize_surface(self, model):
        super(SinglePlayerView, self).initialize_surface(model)
        title_widget = LabelWidget("Single Player", 36, Colors.BLACK)

        surface_center = self.surface.get_rect().center
        title_center = title_widget.rect.center

        self.surface.blit(title_widget.image, (surface_center[0]-title_center[0], 0))


class OptionsView(AbstractView):
    def __init__(self, backing_model):
        super(OptionsView, self).__init__(backing_model=backing_model, bg_color=Colors.GREEN)

    def initialize_surface(self, model):
        super(OptionsView, self).initialize_surface(model)
        title_widget = LabelWidget("Options", 36, Colors.BLACK)

        surface_center = self.surface.get_rect().center
        title_center = title_widget.rect.center

        self.surface.blit(title_widget.image, (surface_center[0]-title_center[0], 0))