from controller.multiplayer.MultiplayerOptionsController import MultiplayerOptionsController
from models.entities.MenuOptionEntity import MenuOptionEntity

class MultiplayerEntity(MenuOptionEntity):
    def __init__(self):
        super(MultiplayerEntity, self).__init__("Multiplayer", next_controller_class=MultiplayerOptionsController)