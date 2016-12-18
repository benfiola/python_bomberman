from .keymap import KeyMap, SDL2KeyMap

class Event(object):
    def __init__(self):
        pass


class Quit(Event):
    def __init__(self):
        super().__init__()


class KeyInputEvent(Event, KeyMap):
    def __init__(self, key_code):
        super().__init__()
        self.key_code = key_code

    @staticmethod
    def convert_from_sdl2(key_code):
        if key_code in SDL2KeyMap.MAP:
            return SDL2KeyMap.MAP[key_code]
        return None


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

