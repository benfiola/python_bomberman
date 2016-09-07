from ..maps import MapLoader


class ClientConfiguration(object):
    def __init__(self):
        self.screen_size = (800, 600)
        self.game_name = "Bomberman"


class GameConfiguration(object):
    def __init__(self):
        self.map_name = "map.txt"
        self.map = MapLoader(self.map_name).load()


class HostConfiguration(object):
    def __init__(self, socket_data=('localhost', 20001)):
        self.socket_data = socket_data

client_configuration = ClientConfiguration()
game_configuration = GameConfiguration()
host_configuration = HostConfiguration()


def get_default_game_configuration():
    return game_configuration
