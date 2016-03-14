from pygame import display

from pygame import Surface

from colors import *
from components import *
from animations import *


class AbstractView(object):
    VIEW_TRANSITION_TIME = 100

    def __init__(self, backing_model, bg_color=Colors.BLACK):
        self.surface = None
        self.backing_model = backing_model
        self.model_sprite_dict = {}
        self.containers = []
        self.bg_color = bg_color

    # initialize_surface is called prior to a view transition
    # it basically prepares a screen
    def initialize_surface(self):
        curr_surface = display.get_surface()
        self.surface = Surface(curr_surface.get_size())
        self.surface.fill(self.bg_color)

    # called on every cycle to update the current view
    def update(self):
        rects = []
        for container in self.containers:
            for container_layer_index in container.layers():
                for sprite in container.get_sprites_from_layer(container_layer_index):
                    sprite.update()
            rects.extend(container.draw(display.get_surface()))
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
        start_time = time.time() * 1000
        duration = (time.time() * 1000) - start_time
        width = display.get_surface().get_size()[0]
        old_surface = display.get_surface().copy()

        while duration < AbstractView.VIEW_TRANSITION_TIME:
            progress = duration / AbstractView.VIEW_TRANSITION_TIME
            x_offset = (-width) + (width * progress)
            old_surface_x_offset = x_offset + width
            display.get_surface().blit(old_surface, (old_surface_x_offset, 0))
            display.get_surface().blit(self.surface, (x_offset, 0))
            display.flip()
            duration = (time.time() * 1000) - start_time
        display.get_surface().blit(self.surface, (0, 0))
        display.flip()

    # same as above, but in opposite direction.  could generalize this, am lazy.
    def slide_left(self):
        start_time = time.time() * 1000
        duration = (time.time() * 1000) - start_time
        width = display.get_surface().get_size()[0]
        old_surface = display.get_surface().copy()

        while duration < AbstractView.VIEW_TRANSITION_TIME:
            progress = duration / AbstractView.VIEW_TRANSITION_TIME
            x_offset = width - (width * progress)
            old_surface_x_offset = x_offset - width
            display.get_surface().blit(old_surface, (old_surface_x_offset, 0))
            display.get_surface().blit(self.surface, (x_offset, 0))
            display.flip()
            duration = (time.time() * 1000) - start_time
        display.get_surface().blit(self.surface, (0, 0))
        display.flip()


class MainMenuView(AbstractView):
    def __init__(self, backing_model):
        super(MainMenuView, self).__init__(backing_model=backing_model, bg_color=Colors.BLUE)
        self.title = None
        self.container = None
        self.selection = None

    def initialize_surface(self):
        super(MainMenuView, self).initialize_surface()
        surface_center = self.surface.get_rect().center
        surface_size = self.surface.get_rect().size

        title = TextContainer("Main Menu", 48, Colors.WHITE, self.bg_color)
        title.set_midtop((surface_center[0], 0))

        options = []
        for option_model in self.backing_model.options:
            component = TextComponent(option_model.text, 36, Colors.WHITE, Colors.BLACK)
            self.model_sprite_dict[option_model] = component
            options.append(component)
        menu = MenuContainer(options, Colors.BLACK, Colors.RED, self.backing_model.selection)
        menu.set_midbottom((surface_center[0], surface_size[1] - 36), shift_y=True)
        self.model_sprite_dict[self.backing_model.selection] = menu.selection
        self.containers.extend([title, menu])

    def option_change(self):
        selection_model = self.backing_model.selection
        selection_sprite = self.model_sprite_dict[selection_model]
        target_sprite = self.model_sprite_dict[selection_model.curr_selection]
        selection_sprite.animation_data = SlideAnimationData(100, selection_sprite.rect.topleft,
                                                             target_sprite.rect.topleft)


class TitleScreenView(AbstractView):
    def __init__(self, backing_model):
        super(TitleScreenView, self).__init__(backing_model=backing_model, bg_color=Colors.RED)
        self.title = None
        self.subtext = None

    def initialize_surface(self):
        super(TitleScreenView, self).initialize_surface()
        surface_center = self.surface.get_rect().center
        surface_size = self.surface.get_rect().size

        title = TextContainer("Bomberman", 72, Colors.WHITE, self.bg_color)
        subtext = TextContainer("Press enter to continue", 36, Colors.WHITE, self.bg_color)
        title.set_midtop((surface_center[0], 0))
        subtext.set_midbottom((surface_center[0], surface_size[1]))
        self.containers.extend([title, subtext])


class MultiplayerView(AbstractView):
    def __init__(self, backing_model):
        super(MultiplayerView, self).__init__(backing_model, bg_color=Colors.WHITE)
        surface_center = self.surface.get_rect().center

        title = TextContainer("Multiplayer View", 48, Colors.WHITE, self.bg_color)
        title.set_midtop((surface_center[0], 0))
        self.containers.extend([title])


class MultiplayerOptionsView(AbstractView):
    def __init__(self, backing_model):
        super(MultiplayerOptionsView, self).__init__(backing_model=backing_model, bg_color=Colors.GRAY)

    def initialize_surface(self):
        super(MultiplayerOptionsView, self).initialize_surface()
        surface_center = self.surface.get_rect().center

        title = TextContainer("Multiplayer Options View", 48, Colors.WHITE, self.bg_color)
        title.set_midtop((surface_center[0], 0))
        self.containers.extend([title])


class SinglePlayerOptionsView(AbstractView):
    def __init__(self, backing_model):
        super(SinglePlayerOptionsView, self).__init__(backing_model=backing_model, bg_color=Colors.WHITE)

    def initialize_surface(self):
        super(SinglePlayerOptionsView, self).initialize_surface()
        surface_center = self.surface.get_rect().center

        title = TextContainer("Single Player Options View", 48, Colors.BLACK, self.bg_color)
        title.set_midtop((surface_center[0], 0))
        self.containers.extend([title])


class SinglePlayerView(AbstractView):
    def __init__(self, backing_model):
        super(OptionsView, self).__init__(backing_model=backing_model, bg_color=Colors.RED)

    def initialize_surface(self):
        super(SinglePlayerView, self).initialize_surface()
        surface_center = self.surface.get_rect().center

        title = TextContainer("Single Player View", 48, Colors.WHITE, self.bg_color)
        title.set_midtop((surface_center[0], 0))
        self.containers.extend([title])


class OptionsView(AbstractView):
    def __init__(self, backing_model):
        super(OptionsView, self).__init__(backing_model=backing_model, bg_color=Colors.GREEN)

    def initialize_surface(self):
        super(OptionsView, self).initialize_surface()
        surface_center = self.surface.get_rect().center

        title = TextContainer("Options View", 48, Colors.WHITE, self.bg_color)
        title.set_midtop((surface_center[0], 0))
        self.containers.extend([title])
