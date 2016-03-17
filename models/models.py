from entities.mainmenu import *
from configuration import configuration


class AbstractModel(object):
    def __init__(sellf):
        pass


class MainMenuModel(AbstractModel):
    def __init__(self):
        super(MainMenuModel, self).__init__()
        self.options = [SinglePlayerEntity(), MultiplayerEntity(), OptionsEntity(), ExitEntity()]
        self.selection = MenuSelectionEntity(self.options[0], 0)

    def next_option(self):
        self.selection.prev_selection = self.selection.curr_selection
        self.selection.sel_index += 1
        if self.selection.sel_index >= len(self.options):
            self.selection.sel_index = 0
        self.selection.curr_selection = self.options[self.selection.sel_index]

    def previous_option(self):
        self.selection.prev_selection = self.selection.curr_selection
        self.selection.sel_index -= 1
        if self.selection.sel_index < 0:
            self.selection.sel_index = (len(self.options) - 1)
        self.selection.curr_selection = self.options[self.selection.sel_index]

    def get_selection(self):
        return self.selection.curr_selection


class OptionsModel(AbstractModel):
    def __init__(self):
        super(OptionsModel, self).__init__()
        self.options = []
        for key in configuration.dict:
            curr_config = configuration.dict[key]
            if curr_config.options is not None:
                self.options.append(PredefinedConfigurationEntity(curr_config.key, curr_config.text, curr_config.value,
                                                                  curr_config.options))
            else:
                self.options.append(InputConfigurationEntity(curr_config.key, curr_config.text, curr_config.value))
        self.selection = MenuSelectionEntity(self.options[0], 0)

    def next_option(self):
        self.selection.prev_selection = self.selection.curr_selection
        self.selection.sel_index += 1
        if self.selection.sel_index >= len(self.options):
            self.selection.sel_index = 0
        self.selection.curr_selection = self.options[self.selection.sel_index]

    def previous_option(self):
        self.selection.prev_selection = self.selection.curr_selection
        self.selection.sel_index -= 1
        if self.selection.sel_index < 0:
            self.selection.sel_index = (len(self.options) - 1)
        self.selection.curr_selection = self.options[self.selection.sel_index]

    def next_value(self):
        if isinstance(self.selection.curr_selection, PredefinedConfigurationEntity):
            self.selection.curr_selection.next_value()

    def previous_value(self):
        if isinstance(self.selection.curr_selection, PredefinedConfigurationEntity):
            self.selection.curr_selection.previous_value()

    def handle_alphanumeric_input(self, input):
        if isinstance(self.selection.curr_selection, InputConfigurationEntity):
            self.selection.curr_selection.handle_input(input)


class SinglePlayerModel(AbstractModel):
    def __init__(self):
        super(SinglePlayerModel, self).__init__()


class SinglePlayerOptionsModel(AbstractModel):
    def __init__(self):
        super(SinglePlayerOptionsModel, self).__init__()


class MultiplayerModel(AbstractModel):
    def __init__(self):
        super(MultiplayerModel, self).__init__()


class MultiplayerOptionsModel(AbstractModel):
    def __init__(self):
        super(MultiplayerOptionsModel, self).__init__()


class TitleScreenModel(AbstractModel):
    def __init__(self):
        super(TitleScreenModel, self).__init__()
