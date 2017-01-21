from client.graphics.views import *


class MainMenuView(View):
    BACKGROUND = "background"
    TITLE = "title"
    MENU_CONTAINER = "menu-container"
    MENU_SELECTION = "menu-selection"
    MENU_SINGLE_PLAYER = "menu-single-player"
    MENU_MULTI_PLAYER = "menu-multi-player"
    MENU_OPTIONS = "menu-options"
    MENU_EXIT = "menu-exit"
    MENU_MASK = "menu-mask"

    def __init__(self, window):
        super().__init__(window)

    def entity_added(self, entity, view_qualifier):
        if view_qualifier == self.BACKGROUND:
            self.sprite_factory.color(entity, self.layout, colors.BLUE)
        if view_qualifier == self.MENU_MASK:
            old_depth = self.layout.depth
            self.layout.depth = 10
            s = self.sprite_factory.color(entity, self.layout, colors.BLUE, clear=True)
            self.layout.depth = old_depth
            import sdl2.ext
            sdl2.ext.fill(s, colors.CLEAR, self.layout.container(tag="title").area())
            sdl2.ext.fill(s, colors.CLEAR, self.layout.container(tag="menu-container").area())
        if view_qualifier == self.TITLE:
            self.sprite_factory.text(entity, "Bomberman", self.layout.container(tag="title"), colors.WHITE)
        if view_qualifier == self.MENU_SELECTION:
            layout = self.layout.container(tag="selection-layer").container(location=(0, entity.selected_index))
            self.sprite_factory.color(entity, layout, colors.RED)
        if view_qualifier == self.MENU_CONTAINER:
            # get our number of options
            num_options = len(entity.entities)

            # get our menu container
            # set the dimensions
            # and then create two children layers -
            # one for selection, one for menu options
            container = self.layout.container(tag="menu-container")
            container.set_dimensions((1, num_options))
            container.create(tag="selection-layer").create(tag="menu-option-layer")
            self.sprite_factory.color(entity, container, colors.BLACK)

            menu_grid = container.container(tag="menu-option-layer")
            for index, menu_option in enumerate(entity.entities):
                layout = menu_grid.container(location=(0, index))
                option_qualifier = menu_option._view_qualifier
                if option_qualifier == self.MENU_SINGLE_PLAYER:
                    self.sprite_factory.text(menu_option, "Single-player", layout, colors.WHITE)
                if option_qualifier == self.MENU_MULTI_PLAYER:
                    self.sprite_factory.text(menu_option, "Multi-player", layout, colors.WHITE)
                if option_qualifier == self.MENU_OPTIONS:
                    self.sprite_factory.text(menu_option, "Options", layout, colors.WHITE)
                if option_qualifier == self.MENU_EXIT:
                    self.sprite_factory.text(menu_option, "Exit", layout, colors.WHITE)

    def entity_changed(self, entity, view_qualifier, key, value, old_value):
        if view_qualifier == self.MENU_SELECTION:
            menu_grid = self.layout.container(tag="menu-option-layer")
            num_rows = menu_grid.dimensions[1]
            grid_per_second = (0, 1)
            chain = None
            primary_target = menu_grid.container(location=(0, entity.selected_index))
            if old_value == num_rows-1 and value == 0:
                secondary_target = primary_target
                secondary_starting_location = menu_grid.container(location=(0, -1))
                primary_target = menu_grid.container(location=(0, num_rows))
                grid_per_second = (grid_per_second[0], grid_per_second[1]*2)
                chain = self.generate_animation_chain(entity, secondary_target, grid_per_second, starting_layout=secondary_starting_location)
            if old_value == 0 and value == num_rows - 1:
                secondary_target = primary_target
                secondary_starting_location = menu_grid.container(location=(0, num_rows))
                primary_target = menu_grid.container(location=(0, -1))
                grid_per_second = (grid_per_second[0], grid_per_second[1]*2)
                chain = self.generate_animation_chain(entity, secondary_target, grid_per_second, starting_layout=secondary_starting_location)
            self.animate(entity, primary_target, grid_per_second, chain=chain)



