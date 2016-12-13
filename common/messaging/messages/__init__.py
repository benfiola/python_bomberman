import uuid
import struct


class BaseMessage(object):
    def __init__(self):
        self.uuid = str(uuid.uuid4())
        self.requires_response = False


class BaseRequest(BaseMessage):
    def __init__(self):
        super().__init__()
        self.requires_response = True


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
    def __init__(self, request_id, error):
        super().__init__(request_id)
        self.error = error


class RequestSuccess(BaseResponse):
    def __init__(self, request_id):
        super().__init__(request_id)


class IncomingRequest(BaseMessage):
    def __init__(self, size):
        super().__init__()
        self.size = size

    def __getstate__(self):
        """
        We have a problem - we need this request to be a constant size as its required to
        fetch subsequent requests off of the size attribute.

        However, when pickling integers (like our size attribute), I've found that they tend
        to have variable lengths - for example, an IncomingRequest with size attribute 240 might result
        in a pickled IncomingRequest of 148 bytes.  However, an Incoming request of size attribute sys.maxsize
        might result in a pickled IncomingRequest of 151 bytes.

        This has a direct effect on how we pass messages - tell a socket to only read 148 bytes when our
        IncomingRequest is 151 bytes, and the pickler will fail with an EOF error.  Tell a socket to read
        151 bytes when our IncomingRequest is 148 bytes, and we'll accidentally read 3 bytes of the next
        message on the socket, causing an error when we attempt to read the next message.

        This means we have to convert the integer into a format that will be of a consistent
        size.
        :return:
        """
        new_dict = self.__dict__.copy()
        int_size = self.size
        del new_dict['size']
        bytes_size = struct.pack('!I', int_size)
        new_dict['size'] = bytes_size
        return new_dict

    def __setstate__(self, state):
        self.__dict__.update(state)
        bytes_size = self.size
        int_size = struct.unpack('!I', bytes_size)[0]
        self.size = int_size
