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


class MenuSelectionEntity(AbstractEntity):
    def __init__(self, curr_selection, index):
        super(MenuSelectionEntity, self).__init__()
        self.prev_selection = None
        self.curr_selection = curr_selection
        self.sel_index = index


class OptionValueEntity(AbstractEntity):
    def __init__(self, text, value):
        super(OptionValueEntity, self).__init__()
        self.text = text
        self.value = value


class OptionChoiceEntity(AbstractEntity):
    def __init__(self, text, available_options, selection):
        super(OptionChoiceEntity, self).__init__()
        self.text = text
        self.available_options = available_options
        self.selection = selection
