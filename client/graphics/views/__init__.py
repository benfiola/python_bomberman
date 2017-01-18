import client.graphics.layouts as layouts
import client.graphics.sprite_factories as sprite_factories
import client.graphics.colors as colors
import client.entities.components as components
import os
import sys


class View(object):
    def __init__(self, window, layout_file="layout.xml"):
        self.window = window
        self.layout = layouts.LayoutParser.generate_layout(self._get_layout_path(layout_file))
        self.sprite_factory = sprite_factories.BaseSpriteFactory()
        self.entities = {}

    def _get_layout_path(self, layout_file):
        module_file = sys.modules[self.__module__].__file__
        module_path = os.path.dirname(os.path.abspath(module_file))
        return os.path.join(module_path, layout_file)

    def set_up(self):
        self.layout.finalize(self.window.size)

    def on_entity_add(self, entity):
        if getattr(entity, "_view_qualifier", None):
            view_qualifier = getattr(entity, "_view_qualifier")
            self.entities[entity._uuid] = entity
            self.entity_added(entity, view_qualifier)

    def entity_added(self, entity, view_qualifier):
        pass

    def entity_changed(self, entity, view_qualifier, key, value, old_value):
        pass

    def on_entity_change(self, entity, key, value, old_value):
        view_qualifier = getattr(entity, "_view_qualifier")
        self.entity_changed(entity, view_qualifier, key, value, old_value)

    def animate(self, entity, layout, grid_per_second, boundary=None):
        """
        helper function for animations, which is effectively assigning
        an animation component to an entity's _sdl2_entity.

        we specify the velocity of the animation in 'grids_per_second',
        meaning 'how many grid spaces in the container will this traverse
        in one second'.  this is because distance will scale with screen
        size, and using a typical duration will result in inconsistent
        animations depending on where the entity currently is.
        :param entity:
        :param layout:
        :param grid_per_second:
        :return:
        """
        v_x = (layout.grid_size[0] * grid_per_second[0])
        v_y = (layout.grid_size[0] * grid_per_second[1])
        clipping_container = None
        if True:
            if entity._sdl2_entity.sprite.position[0] > layout.absolute_location[0]:
                v_x = -v_x
            if entity._sdl2_entity.sprite.position[1] > layout.absolute_location[1]:
                v_y = -v_y
        else:
            clipping_container = (*boundary.absolute_location, *boundary.absolute_size)

        entity._sdl2_entity.animation = components.Animation(
            target_coords=layout.absolute_location,
            velocity_coords=(v_x, v_y),
            clipping_container=clipping_container
        )