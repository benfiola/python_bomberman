import controller
from models.entities.entities import *


class MultiplayerEntity(MenuEntity):
    def __init__(self):
        super(MultiplayerEntity, self).__init__("Multiplayer", next_controller_class=controller.MultiplayerOptionsController)


class ExitEntity(MenuEntity):
    def __init__(self):
        super(ExitEntity, self).__init__("Exit", exit_selection=True)


class OptionsEntity(MenuEntity):
    def __init__(self):
        super(OptionsEntity, self).__init__("Options", next_controller_class=controller.OptionsController)


class SinglePlayerEntity(MenuEntity):
    def __init__(self):
        super(SinglePlayerEntity, self).__init__("Single Player", next_controller_class=controller.SinglePlayerOptionsController)