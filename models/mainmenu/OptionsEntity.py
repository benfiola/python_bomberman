from controller.options.OptionsController import OptionsController
from models.entities.MenuOptionEntity import MenuOptionEntity

class OptionsEntity(MenuOptionEntity):
    def __init__(self):
        super(OptionsEntity, self).__init__("Options", next_controller_class=OptionsController)