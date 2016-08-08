

# A connection request is issued from the client to the host asking the host to complete
# a bidirectional communication channel between client and host via socket.
class BaseMessage(object):
    def __init__(self, data=None):
        self.data = data

    def __str__(self):
        return "%s:[%s]" % (self.__class__.__name__, str(self.data))


class ConnectionRequest(BaseMessage):
    def __init__(self, socket_data):
        super().__init__(socket_data)


class PrintMessage(BaseMessage):
    def __init__(self, message):
        super().__init__(message)


class SuccessfulResponse(BaseMessage):
    def __init__(self):
        super().__init__()


class FailedResponse(BaseMessage):
    def __init__(self, error):
        super().__init__(error)


class InitializeGame(BaseMessage):
    def __init__(self, configuration):
        super().__init__(configuration)


class StartGame(BaseMessage):
    def __init__(self):
        super().__init__()
