from .keymap import KeyMap, SDL2KeyMap

class Event(object):
    def __init__(self):
        pass


class Quit(Event):
    def __init__(self):
        super().__init__()


class KeyInputEvent(Event, KeyMap, SDL2KeyMap):
    def __init__(self, key_code):
        super().__init__()
        self.key_code = key_code


class KeyInputDown(KeyInputEvent):
    def __init__(self, key_code):
        super().__init__(key_code)


class SendRequest(Event):
    def __init__(self, request):
        super().__init__()
        self.request = request


class KeyInputUp(KeyInputEvent):
    def __init__(self, key_code):
        super().__init__(key_code)


class ControllerTransition(Event):
    def __init__(self, controller_class):
        super().__init__()
        self.controller_class = controller_class


