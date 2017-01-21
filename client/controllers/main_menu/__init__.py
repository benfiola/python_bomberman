from client.controllers import *
import client.graphics.views.main_menu as view


class MainMenuController(Controller):
    def __init__(self, client):
        super().__init__(client, view.MainMenuView)
        self.selection = None
        self.menu_options = None

    def set_up(self):
        self.menu_options = [
            entities.ClientEntity(self, uuid="single-player", view_qualifier=view.MainMenuView.MENU_SINGLE_PLAYER),
            entities.ClientEntity(self, uuid="multi-player", view_qualifier=view.MainMenuView.MENU_MULTI_PLAYER),
            entities.ClientEntity(self, uuid="options", view_qualifier=view.MainMenuView.MENU_OPTIONS),
            entities.ClientEntity(self, uuid="exit", view_qualifier=view.MainMenuView.MENU_EXIT)
        ]
        entities.ClientEntity(self, view_qualifier=view.MainMenuView.BACKGROUND)
        entities.ClientEntity(self, view_qualifier=view.MainMenuView.TITLE)
        entities.MenuContainer(self, self.menu_options, view_qualifier=view.MainMenuView.MENU_CONTAINER)
        entities.ClientEntity(self, view_qualifier=view.MainMenuView.MENU_MASK)
        self.selection = entities.SelectionEntity(self, view_qualifier=view.MainMenuView.MENU_SELECTION)

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.UP:
            self.previous_option()
        if key_code == events.KeyInputEvent.DOWN:
            self.next_option()
        if key_code == events.KeyInputEvent.RETURN:
            self.select_option()
        if key_code == events.KeyInputEvent.ESC:
            import client.controllers.intro as controller
            self.client.add_event(events.ControllerTransition(controller.IntroController))

    def next_option(self):
        self.selection.selected_index = (self.selection.selected_index + 1) % (len(self.menu_options))

    def previous_option(self):
        self.selection.selected_index = (self.selection.selected_index - 1) % (len(self.menu_options))

    def select_option(self):
        selection = self.menu_options[self.selection.selected_index]
        if selection._uuid == "single-player":
            import client.controllers.single_player_options as controller
            self.client.add_event(events.ControllerTransition(controller.SinglePlayerOptionsController))
        if selection._uuid == "multi-player":
            import client.controllers.multi_player_options as controller
            self.client.add_event(events.ControllerTransition(controller.MultiPlayerOptionsController))
        if selection._uuid == "options":
            import client.controllers.options as controller
            self.client.add_event(events.ControllerTransition(controller.OptionsController))
        if selection._uuid == "exit":
            self.client.add_event(events.Quit())