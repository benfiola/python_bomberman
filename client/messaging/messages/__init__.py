class BaseMessage(object):
    def __init__(self):
        pass


class IdentifyRequest(BaseMessage):
    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id


class RequestFail(BaseMessage):
    def __init__(self, data):
        super().__init__()
        self.data = data


class RequestSuccess(BaseMessage):
    def __init__(self):
        super().__init__()
