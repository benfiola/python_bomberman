from common.custom_events import *


class InitializeGameData(CustomEvent):
    def __init__(self, game_board):
        super().__init__()
        self.game_board = game_board


class UpdateGameData(CustomEvent):
    def __init__(self, update_data):
        super().__init__()
        self.update_data = update_data


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


class QuitEvent(CustomEvent):
    def __init__(self):
        super().__init__()

