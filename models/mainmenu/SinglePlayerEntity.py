from controller.singleplayer.SinglePlayerOptionsController import SinglePlayerOptionsController
from models.entities.MenuOptionEntity import MenuOptionEntity

class SinglePlayerEntity(MenuOptionEntity):
    def __init__(self):
        super(SinglePlayerEntity, self).__init__("Single Player", next_controller_class=SinglePlayerOptionsController)