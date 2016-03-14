from entities.mainmenu import *


class AbstractModel(object):
    def __init__(sellf):
        pass


class MainMenuModel(AbstractModel):
    def __init__(self):
        super(MainMenuModel, self).__init__()
        sel_index = 0
        self.options = [SinglePlayerEntity(), MultiplayerEntity(), OptionsEntity(), ExitEntity()]
        self.selection = MenuOptionSelectionEntity(self.options[sel_index], sel_index)

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
