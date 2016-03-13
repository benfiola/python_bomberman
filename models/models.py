from entities.mainmenu import *


class AbstractModel(object):
    def __init__(sellf):
        pass


class MainMenuModel(AbstractModel):
    def __init__(self):
        super(MainMenuModel, self).__init__()
        self.selection = 0
        self.options = [SinglePlayerEntity(), MultiplayerEntity(), OptionsEntity(), ExitEntity()]

    def next_option(self):
        self.selection += 1
        if self.selection >= len(self.options):
            self.selection = 0

    def previous_option(self):
        self.selection -= 1
        if self.selection < 0:
            self.selection = (len(self.options) - 1)

    def get_selection(self):
        return self.options[self.selection]


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
