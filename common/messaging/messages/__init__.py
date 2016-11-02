import uuid


class BaseMessage(object):
    def __init__(self):
        self.id = str(uuid.uuid4())


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
    def __init__(self, request_id):
        super().__init__()
        self.request_id = request_id


class RequestFail(BaseResponse):
    def __init__(self, request_id, message):
        super().__init__(request_id)
        self.message = message


class RequestSuccess(BaseResponse):
    def __init__(self, request_id):
        super().__init__(request_id)


class BaseStatus(BaseMessage):
    def __init__(self):
        super().__init__()


class SocketReceiveTimeout(BaseStatus):
    def __init__(self):
        super().__init__()


class SocketClosed(BaseStatus):
    def __init__(self, target_address):
        super().__init__()
        self.target_address = target_address


class IncomingRequest(BaseMessage):
    def __init__(self, size):
        super().__init__()
        self.size = size
