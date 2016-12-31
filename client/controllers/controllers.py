import sdl2.ext

import client.events as events
import client.entities as entities
import client.graphics as graphics
import client.systems as systems
from common import logging


class Controller(object):
    def __init__(self, client):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = client
        self.world = sdl2.ext.World()
        self.sprite_factory = graphics.BaseSpriteFactory()
        self.window_size = self.client.window.size
        self.entities = {}

    def _key_down(self, event):
        self.on_key_down(event.key_code)

    def _key_up(self, event):
        self.on_key_up(event.key_code)

    def set_up(self):
        self.client.register_event_handler(events.KeyInputDown, self._key_down)
        self.client.register_event_handler(events.KeyInputUp, self._key_up)

    def tear_down(self):
        self.client.remove_event_handlers(self)

    def process(self):
        self.world.process()

    def add_entity(self, entity):
        self.entities[entity.uuid] = entity

    def remove_entity(self, entity):
        self.entities.pop(entity.uuid)

    def on_key_down(self, key_code):
        pass

    def on_key_up(self, key_code):
        pass


class IntroController(Controller):
    def __init__(self, client):
        super().__init__(client)

    def set_up(self):
        super().set_up()
        self.world.add_system(systems.SoftwareRenderer(self.client.window, bg_color=graphics.Colors.BLUE))

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            self.client.add_event(events.Quit())
        if key_code == events.KeyInputEvent.RETURN:
            self.client.add_event(events.ControllerTransition(MainMenuController))


class MainMenuController(Controller):
    def __init__(self, client):
        super().__init__(client)

        font_size = 14

        menu_item_list = [
            "Single-player",
            "Multi-player",
            "Options",
            "Exit"
        ]

        menu_size = (100, len(menu_item_list)*font_size)
        top_left = (int(self.window_size[0]/2 - menu_size[0]/2), int(self.window_size[1]/2 - menu_size[1]/2))
        self.background_entity(menu_size, top_left)
        self.selection = self.selection_entity((100, font_size), top_left)

        menu_item_tl = top_left
        self.menu_items = []
        for item in menu_item_list:
            self.menu_items.append(self.menu_entity(item, menu_item_tl))
            menu_item_tl = (menu_item_tl[0], menu_item_tl[1]+font_size)

    def background_entity(self, size, top_left):
        sprite = self.sprite_factory.from_color(
            graphics.Colors.BLACK, size=size
        )
        sprite.depth = 0
        return entities.BackgroundEntity(self, sprite=sprite, position=top_left)

    def selection_entity(self, size, top_left):
        sprite = self.sprite_factory.from_color(
            graphics.Colors.RED, size=size
        )
        sprite.depth = 1
        return entities.SelectionEntity(self, sprite=sprite, position=top_left)

    def menu_entity(self, text, top_left):
        sprite = self.sprite_factory.from_text(
            text, size=14, color=graphics.Colors.WHITE
        )
        sprite.depth = 2
        return entities.LabelEntity(self, sprite=sprite, position=top_left)

    def set_up(self):
        super().set_up()

        self.client.register_event_handler(events.KeyInputDown, self.on_key_down)
        self.world.add_system(systems.MenuMovementSystem())
        self.world.add_system(systems.SoftwareRenderer(self.client.window, bg_color=graphics.Colors.BLACK))

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            self.client.add_event(events.ControllerTransition(IntroController))
        if key_code == events.KeyInputEvent.UP:
            new_selection = self.selection.selected_index - 1
            if new_selection < 0:
                new_selection = len(self.menu_items) - 1
            self.change_selection(new_selection)
        if key_code == events.KeyInputEvent.DOWN:
            new_selection = self.selection.selected_index + 1
            if new_selection >= len(self.menu_items):
                new_selection = 0
            self.change_selection(new_selection)

    def change_selection(self, index):
        old_index = self.selection.selected_index
        target = self.menu_items[index].sdl2_entity.sprite.position
        velocity = (0, 1)
        if old_index > index:
            velocity = (velocity[0], -velocity[1])
        self.selection.selected_index = index
        self.selection.sdl2_entity.velocity = entities.Velocity(velocity, target)

