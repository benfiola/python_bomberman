class AbstractEntity(object):
    def __init__(self):
        self.sprite_hash = None


class MenuOptionEntity(AbstractEntity):
    def __init__(self, text, next_controller_class=None, exit_selection=False):
        super(MenuOptionEntity, self).__init__()
        self.text = text
        self.next_controller_class = next_controller_class
        self.exit_selection = exit_selection
        pass


class MenuOptionSelectionEntity(AbstractEntity):
    def __init__(self, curr_selection, index):
        self.prev_selection = None
        self.curr_selection = curr_selection
        self.sel_index = index


class SelectableOptionEntity(AbstractEntity):
    def __init__(self, option_text, available_options, selection):
        super(SelectableOptionEntity, self).__init__()
