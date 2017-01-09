import logging
import sdl2.ext
import client.entities as entities
import client.events as events
import client.graphics as graphics
import client.systems as systems
import client.graphics.layouts as layouts
import os
import sys


class Controller(object):
    def __init__(self, client, layout_file="layout.xml"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = client
        self.world = sdl2.ext.World()
        self.sprite_factory = graphics.BaseSpriteFactory()
        self.window_size = self.client.window.size
        self.layout = graphics.LayoutParser.generate_layout(self._get_layout_path(layout_file))
        self.entities = {}

    def _get_layout_path(self, layout_file):
        module_file = sys.modules[self.__module__].__file__
        module_path = os.path.dirname(os.path.abspath(module_file))
        return os.path.join(module_path, layout_file)

    def _key_down(self, event):
        self.on_key_down(event.key_code)

    def _key_up(self, event):
        self.on_key_up(event.key_code)

    def set_up(self):
        self.client.register_event_handler(events.KeyInputDown, self._key_down)
        self.client.register_event_handler(events.KeyInputUp, self._key_up)

    def tear_down(self):
        self.client.remove_event_handlers(self)
        for entity in list(self.entities.values()):
            self.remove_entity(entity)
        self.entities = {}

    def process(self):
        self.world.process()

    def add_entity(self, entity):
        self.entities[entity.uuid] = entity

    def remove_entity(self, entity):
        entity = self.entities.pop(entity.uuid)
        self.world.delete(entity.sdl2_entity)

    def on_key_down(self, key_code):
        pass

    def on_key_up(self, key_code):
        pass

