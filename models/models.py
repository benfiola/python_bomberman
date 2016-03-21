from entities.mainmenu import *
from configuration import configuration


class AbstractModel(object):
    def __init__(sellf):
        pass

class AbstractMenuModel(AbstractModel):
    def __init__(self, options):
        super(AbstractMenuModel, self).__init__()
        self.options = options
        self.selection = SelectionEntity(self.options[0], 0)

    def next_option(self):
        if not isinstance(self.get_selection(), ConfigurationEntity) or (isinstance(self.get_selection(), ConfigurationEntity) and not self.selection.is_active):
            self.selection.prev_selection = self.selection.curr_selection
            self.selection.sel_index += 1
            if self.selection.sel_index >= len(self.options):
                self.selection.sel_index = 0
            self.selection.curr_selection = self.options[self.selection.sel_index]

    def previous_option(self):
        if not isinstance(self.get_selection(), ConfigurationEntity) or (isinstance(self.get_selection(), ConfigurationEntity) and not self.selection.is_active):
            self.selection.prev_selection = self.selection.curr_selection
            self.selection.sel_index -= 1
            if self.selection.sel_index < 0:
                self.selection.sel_index = (len(self.options) - 1)
            self.selection.curr_selection = self.options[self.selection.sel_index]

    def set_selection_active(self):
        self.selection.is_active = True

    def set_selection_inactive(self):
        self.selection.is_active = False

    def next_value(self):
        if isinstance(self.get_selection(), ConfigurationEntity) and self.selection.is_active:
            self.get_selection().next_value()

    def previous_value(self):
        if isinstance(self.get_selection(), ConfigurationEntity) and self.selection.is_active:
            self.get_selection().previous_value()

    def get_selection(self):
        return self.selection.curr_selection


class MainMenuModel(AbstractMenuModel):
    def __init__(self):
        options = [SinglePlayerEntity(), MultiplayerEntity(), OptionsEntity(), ExitEntity()]
        super(MainMenuModel, self).__init__(options)


class OptionsModel(AbstractMenuModel):
    def __init__(self):
        options = []
        for key in configuration.dict:
            curr_config = configuration.dict[key]
            if curr_config.options is not None:
                options.append(PredefinedConfigurationEntity(curr_config.key, curr_config.text, curr_config.value,
                                                                  curr_config.options))
            else:
                options.append(ConfigurationEntity(curr_config.key, curr_config.text, curr_config.value))
        super(OptionsModel, self).__init__(options)

    def next_option(self):
        if not self.selection.is_active:
            super(OptionsModel, self).next_option()

    def previous_option(self):
        if not self.selection.is_active:
            super(OptionsModel, self).previous_option()

    def handle_alphanumeric_input(self, input):
        if isinstance(self.selection.curr_selection, ConfigurationEntity):
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
