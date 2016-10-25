class BaseMessage(object):
    def __init__(self):
        pass


class BaseRequest(BaseMessage):
    def __init__(self):
        super().__init__()


class PrintRequest(BaseRequest):
    def __init__(self, message):
        super().__init__()
        self.message = message


class IdentifyRequest(BaseRequest):
    def __init__(self, client_id, target_address):
        super().__init__()
        self.client_id = client_id
        self.target_address = target_address


class BaseResponse(BaseMessage):
    def __init__(self):
        super().__init__()


class RequestFail(BaseResponse):
    def __init__(self, data):
        super().__init__()
        self.data = data


class RequestSuccess(BaseResponse):
    def __init__(self):
        super().__init__()


class BaseStatus(BaseMessage):
    def __init__(self):
        super().__init__()


class SocketReceiveTimeout(BaseStatus):
    def __init__(self):
        super().__init__()


class SocketClosed(BaseStatus):
    def __init__(self):
        super().__init__()