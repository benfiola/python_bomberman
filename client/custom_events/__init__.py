

class CustomEvent(object):
    def __init__(self):
        pass


class ViewStateChange(CustomEvent):
    def __init__(self, next_state):
        super().__init__()
        self.next_state = next_state


class CreateHost(CustomEvent):
    def __init__(self, configuration):
        super().__init__()
        self.configuration = configuration


class ConnectToHost(CustomEvent):
    def __init__(self, configuration):
        super().__init__()
        self.configuration = configuration


class DisconnectFromHost(CustomEvent):
    def __init__(self):
        super().__init__()


class SendMessage(CustomEvent):
    def __init__(self, message):
        super().__init__()
        self.message = message


class ReceiveMessage(CustomEvent):
    def __init__(self, message):
        super().__init__()
        self.message = message


class QuitEvent(CustomEvent):
    def __init__(self):
        super().__init__()
