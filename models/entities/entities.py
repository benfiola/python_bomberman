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


class InputConfigurationEntity(AbstractEntity):
    def __init__(self, key, text, value):
        self.key = key
        self.text = text
        self.value = value

    def handle_alphanumeric_input(self, input):
        self.value = self.value + input

class PredefinedConfigurationEntity(AbstractEntity):
    def __init__(self, key, text, value, options):
        self.key = key
        self.text = text
        self.value = value
        self.options = options
        self.index = 0
        for x in range(0, len(self.options)):
            if self.options[x] == self.value:
                self.index = x

    def next_value(self):
        self.index += 1
        if self.index >= len(self.options):
            self.index = 0
        self.value = self.options[self.index]

    def previous_value(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1
        self.value = self.options[self.index]


