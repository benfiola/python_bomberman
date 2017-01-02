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

        menu_item_list = [
            entities.LabelEntity(self, "Single-player"),
            entities.LabelEntity(self, "Multi-player"),
            entities.LabelEntity(self, "Options"),
            entities.LabelEntity(self, "Exit"),
        ]

        font_size = 14

        root_layout = graphics.GridLayout((1, 1))
        bg_entity = entities.BackgroundEntity(self)
        menu_container_layout = root_layout.add_child(bg_entity, (0, 0), (1, 1)).create_layout((6, 6))

        menu_container = entities.BackgroundEntity(self)
        menu_layout = menu_container_layout.add_child(menu_container, (1, 1), (4, 4)).create_layout((1, len(menu_item_list)))

        selection = entities.SelectionEntity(self)
        menu_layout.add_child(selection, (0, 0), (1, 1))

        for (index, obj) in enumerate(menu_item_list):
            menu_layout.add_child(obj, (0, index), (1, 1))

        sprite_data = root_layout.finalize(self.client.window.size)
        for entity in sprite_data.keys():
            top_left, dimensions = sprite_data[entity]
            if entity is bg_entity:
                self.add_color_sprite(entity, dimensions, top_left, graphics.colors.Colors.BLUE, 0)
            if entity is menu_container:
                self.add_color_sprite(entity, dimensions, top_left, graphics.colors.Colors.BLACK, 1)
            if entity is selection:
                self.add_color_sprite(entity, dimensions, top_left, graphics.colors.Colors.RED, 2)
            if entity in menu_item_list:
                self.add_text_sprite(entity, entity.text, 14, dimensions, top_left, graphics.colors.Colors.WHITE, 3)

        self.selection = selection
        self.menu_items = menu_item_list

    def add_color_sprite(self, entity, size, top_left, color, depth):
        sprite = self.sprite_factory.from_color(
            color, size=size
        )
        sprite.position = top_left
        sprite.depth = depth
        entity.sdl2_entity.sprite = sprite

    def add_text_sprite(self, entity, text, font_size, dimensions, top_left, color, depth, center_x=True, center_y=True):
        sprite = self.sprite_factory.from_text(
            text, size=font_size, color=color
        )
        sprite.position = top_left
        sprite_size = sprite.size
        if center_y:
            sprite.position = (sprite.position[0], sprite.position[1] + int(dimensions[1]/2 - sprite.size[1]/2))
        if center_x:
            sprite.position = (sprite.position[0] + int(dimensions[0]/2 - sprite.size[0]/2), sprite.position[1])
        sprite.depth = depth
        entity.sdl2_entity.sprite = sprite

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

