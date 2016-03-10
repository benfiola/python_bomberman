from models.entities.AbstractEntity import AbstractEntity
from models.mainmenu.ExitEntity import ExitEntity
from models.mainmenu.MultiplayerEntity import MultiplayerEntity
from models.mainmenu.OptionsEntity import OptionsEntity
from models.mainmenu.SinglePlayerEntity import SinglePlayerEntity

class MainMenuModel(AbstractEntity):
    def __init__(self):
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
