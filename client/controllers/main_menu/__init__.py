from client.controllers import *
import collections


class MainMenuController(Controller):
    def __init__(self, client):
        super().__init__(client)
        self.selection = None
        self.menu_options = collections.OrderedDict()

    def prepare_layout(self):
        self.layout.finalize(self.window_size)

        menu_container = self.layout.container("menu-container")
        container_dimensions = (1, len(self.menu_options))
        menu_container.dimensions = container_dimensions
        menu_container.add_container(layouts.Container((0, 0), (1, 1), tag="menu-selection-container"))
        menu_container.add_container(layouts.Container((0, 0), container_dimensions, dimensions=container_dimensions, tag="menu-options-container"))
        self.layout.finalize(self.window_size)

        for index, menu_option in enumerate(self.menu_options.keys()):
            self.layout.container("menu-options-container").add_container(layouts.Container((0, index), (1, 1), tag=menu_option))

        self.layout.finalize(self.window_size)

    def set_up(self):
        super().set_up()

        # define our menu options using an ordered dict (so the order of insertion is also the order we get when
        # we iterate on the keys
        self.menu_options["menu-single-player"] = entities.LabelEntity(self, "Single-Player", graphics.Colors.WHITE)
        self.menu_options["menu-multi-player"] = entities.LabelEntity(self, "Multi-Player", graphics.Colors.WHITE)
        self.menu_options["menu-options"] = entities.LabelEntity(self, "Options", graphics.Colors.WHITE)
        self.menu_options["menu-exit"] = entities.LabelEntity(self, "Exit", graphics.Colors.WHITE)

        # create our dynamic layout for menu options here
        menu_container = self.layout.container("menu-container")
        container_dimensions = (1, len(self.menu_options))
        menu_container.dimensions = container_dimensions
        menu_container.add_container(layouts.Container((0, 0), (1, 1), tag="menu-selection-container"))
        menu_container.add_container(layouts.Container((0, 0), container_dimensions, dimensions=container_dimensions,
                                                       tag="menu-options-container"))
        for index, menu_option in enumerate(self.menu_options.keys()):
            self.layout.container("menu-options-container").add_container(
                layouts.Container((0, index), (1, 1), tag=menu_option))
        self.layout.finalize(self.window_size)

        background_entity = entities.ColorEntity(self, graphics.Colors.BLUE)
        self.sprite_factory.color(background_entity, self.layout)
        title_entity = entities.LabelEntity(self, "Bomberman", graphics.Colors.WHITE)
        self.sprite_factory.text(title_entity, self.layout.container("title"))
        menu_background_entity = entities.ColorEntity(self, graphics.Colors.BLACK)
        self.sprite_factory.color(menu_background_entity, self.layout.container("menu-container"))
        self.selection = entities.SelectionEntity(self, graphics.Colors.RED)
        self.sprite_factory.color(self.selection, self.layout.container("menu-selection-container"))
        for key in self.menu_options.keys():
            self.sprite_factory.text(self.menu_options[key], self.layout.container(key))

        self.world.add_system(systems.MenuMovementSystem())
        self.world.add_system(systems.SoftwareRenderer(self.client.window))

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            from client.controllers.intro import IntroController
            self.client.add_event(events.ControllerTransition(IntroController))
        if key_code == events.KeyInputEvent.UP:
            self.previous_menu_option()
        if key_code == events.KeyInputEvent.DOWN:
            self.next_menu_option()
        if key_code == events.KeyInputEvent.RETURN:
            self.select_menu_option()

    def previous_menu_option(self):
        new_selection = self.selection.selected_index - 1
        if new_selection < 0:
            new_selection = len(self.menu_options) - 1
        self.change_selection(new_selection)

    def next_menu_option(self):
        new_selection = self.selection.selected_index + 1
        if new_selection >= len(self.menu_options):
            new_selection = 0
        self.change_selection(new_selection)

    def select_menu_option(self):
        key = list(self.menu_options.keys())[self.selection.selected_index]
        if key == "menu-single-player":
            from client.controllers.single_player_options import SinglePlayerOptionsController
            self.client.add_event(events.ControllerTransition(SinglePlayerOptionsController))
        if key == "menu-multi-player":
            from client.controllers.multi_player_options import MultiPlayerOptionsController
            self.client.add_event(events.ControllerTransition(MultiPlayerOptionsController))
        if key == "menu-options":
            from client.controllers.options import OptionsController
            self.client.add_event(events.ControllerTransition(OptionsController))
        if key == "menu-exit":
            self.client.add_event(events.Quit())

    def change_selection(self, index):
        old_index = self.selection.selected_index
        menu_option_container_key = list(self.menu_options.keys())[index]
        selection_size = self.layout.container("menu-selection-container").absolute_size[1]
        target = self.layout.container(menu_option_container_key).absolute_location
        velocity = (0, selection_size)
        if old_index > index:
            velocity = (velocity[0], -velocity[1])
        self.selection.selected_index = index
        self.selection.sdl2_entity.velocity = entities.Velocity(velocity, target)