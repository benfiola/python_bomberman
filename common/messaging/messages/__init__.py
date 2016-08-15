

# A connection request is issued from the client to the host asking the host to complete
# a bidirectional communication channel between client and host via socket.
class BaseMessage(object):
    def __init__(self):
        self.data = MessageData()

    def __str__(self):
        return "%s:[%s]" % (self.__class__.__name__, str(self.data))


class ConnectionRequest(BaseMessage):
    def __init__(self, socket_data):
        super().__init__()
        self.data.socket_data = socket_data


class DisconnectionRequest(BaseMessage):
    def __init__(self, socket_data):
        super().__init__()
        self.data.socket_data = socket_data


class HostShutdownRequest(BaseMessage):
    def __init__(self):
        super().__init__()


class PrintMessageRequest(BaseMessage):
    def __init__(self, message):
        super().__init__()
        self.data.message = message


class SuccessfulResponse(BaseMessage):
    def __init__(self):
        super().__init__()


class FailedResponse(BaseMessage):
    def __init__(self, error):
        super().__init__()
        self.data.error = error


class InitializeGameRequest(BaseMessage):
    def __init__(self, configuration):
        super().__init__()
        self.data.configuration = configuration


class AssignPlayerEntityRequest(BaseMessage):
    def __init__(self):
        super().__init__()


class StartGameRequest(BaseMessage):
    def __init__(self):
        super().__init__()


class ClientGameDataRequest(BaseMessage):
    def __init__(self, game_board):
        super().__init__()
        self.data.game_board = game_board


class MoveEntityRequest(BaseMessage):
    def __init__(self, direction):
        super().__init__()
        self.data.direction = direction


class MessageData(object):
    def __init__(self):
        super().__init__()

    def __getattr__(self, key):
        if key not in ["__getstate__", "__setstate__"]:
            setattr(self, key, None)
        else:
            raise AttributeError(key)




