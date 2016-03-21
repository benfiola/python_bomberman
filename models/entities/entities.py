class AbstractEntity(object):
    def __init__(self):
        self.sprite_hash = None


class MenuEntity(AbstractEntity):
    def __init__(self, text, next_controller_class=None, exit_selection=False):
        super(MenuEntity, self).__init__()
        self.text = text
        self.next_controller_class = next_controller_class
        self.exit_selection = exit_selection
        pass


class SelectionEntity(AbstractEntity):
    def __init__(self, curr_selection, index):
        super(SelectionEntity, self).__init__()
        self.prev_selection = None
        self.curr_selection = curr_selection
        self.is_active = False
        self.sel_index = index


class ConfigurationEntity(AbstractEntity):
    def __init__(self, key, text, value):
        super(ConfigurationEntity, self).__init__()
        self.key = key
        self.text = text
        self.value = value

    def handle_input(self):
        pass

    def next_value(self):
        pass

    def previous_value(self):
        pass


class InputConfiugrationEntity(ConfigurationEntity):
    def __init__(self, key, text, value):
        super(InputConfiugrationEntity, self).__init__(key, text, value)

    def handle_input(self, input):
        self.value += input


class PredefinedConfigurationEntity(ConfigurationEntity):
    def __init__(self, key, text, value, options):
        super(PredefinedConfigurationEntity, self).__init__(key, text, value)
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
