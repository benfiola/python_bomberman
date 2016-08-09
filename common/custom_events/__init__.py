

class CustomEvent(object):
    def __init__(self):
        pass


class SendMessage(CustomEvent):
    def __init__(self, message):
        super().__init__()
        self.message = message