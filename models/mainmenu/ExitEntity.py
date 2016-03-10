from models.entities.MenuOptionEntity import MenuOptionEntity

class ExitEntity(MenuOptionEntity):
    def __init__(self):
        super(ExitEntity, self).__init__("Exit", exit_selection=True)