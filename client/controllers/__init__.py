import logging
import sdl2.ext
import client.entities as entities
import client.events as events
import client.systems as systems

class Controller(object):
    def __init__(self, client, view_class):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = client
        self.world = sdl2.ext.World()
        self.view = view_class(self.client.window)
        self.entities = {}

    def _key_down(self, event):
        self.on_key_down(event.key_code)

    def _key_up(self, event):
        self.on_key_up(event.key_code)

    def _set_up(self):
        self.view.set_up()
        self.set_up()

        self.client.register_event_handler(events.KeyInputDown, self._key_down)
        self.client.register_event_handler(events.KeyInputUp, self._key_up)

        self.world.add_system(systems.AnimationSystem())
        self.world.add_system(systems.SoftwareRenderer(self.client.window))

    def _on_entity_change(self, entity, key, value):
        self.view.on_entity_change(entity, key, value)

    def set_up(self):
        pass

    def tear_down(self):
        self.client.remove_event_handlers(self)
        for entity in list(self.entities.values()):
            self.remove_entity(entity)
        for system in list(self.world.systems):
            self.world.remove_system(system)
        self.entities = {}

    def process(self):
        self.world.process()

    def add_entity(self, entity):
        self.entities[entity._uuid] = entity
        self.view.add_entity(entity)

    def remove_entity(self, entity):
        entity = self.entities.pop(entity.uuid)
        self.world.delete(entity.sdl2_entity)

    def on_key_down(self, key_code):
        pass

    def on_key_up(self, key_code):
        pass

