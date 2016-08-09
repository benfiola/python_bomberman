from common.custom_events import *


class ClientEvent(CustomEvent):
    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id


class ClientValidatedEvent(ClientEvent):
    def __init__(self, client_id):
        super().__init__(client_id)


class ClientConnectionEvent(ClientEvent):
    def __init__(self, client_id, socket_data):
        super().__init__(client_id)
        self.socket_data = socket_data


class ClientDisconnectionEvent(ClientEvent):
    def __init__(self, client_id, socket_data):
        super().__init__(ClientEvent)
        self.socket_data = socket_data


class InitializeGameEvent(ClientValidatedEvent):
    def __init__(self, client_id, game_configuration):
        super().__init__(client_id)
        self.game_configuration = game_configuration


class StartGameEvent(ClientEvent):
    def __init__(self, client_id):
        super().__init__(client_id)


class QuitEvent(ClientValidatedEvent):
    def __init__(self, client_id):
        super().__init__(client_id)
