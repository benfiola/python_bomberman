
class ClientConfiguration(object):
    def __init__(self):
        self.screen_size = (800, 600)
        self.game_name = "Bomberman"
        self.socket_data = ('localhost', 20000)

class GameConfiguration(object):
    def __init__(self):
        self.map_name = "map.txt"

class HostConfiguration(object):
    def __init__(self):
        self.socket_data = ('localhost', 20001)

client_configuration = ClientConfiguration()
game_configuration = GameConfiguration()
host_configuration = HostConfiguration()

def get_default_game_configuration():
    return game_configuration