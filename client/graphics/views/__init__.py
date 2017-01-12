import client.graphics.layouts as layouts
import client.graphics.sprite_factories as sprite_factories
import client.graphics.colors as colors
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
        self.prepare_layout()
        self.layout.finalize(self.window.size)

    def prepare_layout(self):
        pass

    def add_entity(self, entity):
        if getattr(entity, "_view_qualifier", None):
            view_qualifier = getattr(entity, "_view_qualifier")
            self.entities[entity._uuid] = entity
            self.on_entity_add(entity, view_qualifier)

    def on_entity_add(self, entity, view_qualifier):
        pass

    def on_entity_change(self, entity, key, value):
        pass



