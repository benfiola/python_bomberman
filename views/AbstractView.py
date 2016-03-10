from pygame import display
from pygame import Surface
from views.Colors import Colors
from time import time

# every view extends from this class
# currently every view gets a copy of a surface - this allows
# views to draw themselves to something (that isn't the main display)
# so they can partially blit themselves during view transitions.
# and simply copy themselves over to the main surface once the animation
# is finished.
# layer groups are part of every AbstractView.  the understanding is that they
# shouldn't overlap, because if they do, the results will be unpredictable.
# they allow us to more easily update our view on every cycle (and will be
# somewhat more performant if we ever move to LayeredDirty)
class AbstractView(object):
    VIEW_TRANSITION_TIME = 100

    def __init__(self, bg_color=Colors.BLACK):
        self.surface = None
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
            duration = (time()*1000) - start_time
        display.get_surface().blit(self.surface, (0, 0))
        display.flip()

    # same as above, but in opposite direction.  could generalize this, am lazy.
    def slide_left(self):
        start_time = time() * 1000
        duration = (time()*1000) - start_time
        width = display.get_surface().get_size()[0]
        old_surface = display.get_surface().copy()

        while duration < AbstractView.VIEW_TRANSITION_TIME:
            progress = duration / AbstractView.VIEW_TRANSITION_TIME
            x_offset = width-(width*progress)
            old_surface_x_offset = x_offset - width
            display.get_surface().blit(old_surface, (old_surface_x_offset, 0))
            display.get_surface().blit(self.surface, (x_offset, 0))
            display.flip()
            duration = (time()*1000) - start_time
        display.get_surface().blit(self.surface, (0, 0))
        display.flip()


