import socketserver, socket, threading, pickle, logging
from .messages import *
from common.logging import get_logger


class MessageBus(object):
    def __init__(self, source, response_callback):
        self.shutting_down = False
        self.logger = get_logger(self)
        self.source = source
        self.response_callback = response_callback
        self.socket = None
        self.server = socketserver.TCPServer(self.source, self.generate_handler())
        self.server_thread = threading.Thread(name=self.get_thread_name(), target=self.server.serve_forever)
        self.server_thread.start()

    def close_socket(self):
        if self.socket is not None:
            self.logger.debug("Closing message bus socket")
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None

    def shut_down(self):
        self.logger.debug("Shutting down message bus")
        self.close_socket()
        self.server.shutdown()

    def get_thread_name(self):
        import inspect
        stack = inspect.stack()
        calling_obj = stack[2][0].f_locals["self"]
        return "%s-MessageBus-SocketServer" % str(calling_obj)

    def connect(self, target):
        if self.socket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(target)

    def send_message(self, data):
        self.logger.debug("Sending message %s" % (str(data)))
        # send data
        self.socket.sendall(pickle.dumps(data))
        # receive response
        r_data = self.socket.recv(1024).strip()
        response = pickle.loads(r_data)
        self.logger.debug("Receiving response %s" % (str(response)))
        if isinstance(response, FailedResponse):
            if isinstance(response.data, Exception):
                raise response.data
            if isinstance(response.data, str):
                raise Exception(response.data)

    def receive_message(self, message):
        data = pickle.loads(message)
        self.logger.debug("Receiving message %s" % (str(data)))
        self.response_callback(data)

    def generate_handler(self):
        bus = self

        class RequestHandler(socketserver.BaseRequestHandler):
            def __init__(self, *args, **kwargs):
                self.logger = get_logger(self)
                super().__init__(*args, **kwargs)

            def handle(self):
                while not bus.shutting_down:
                    try:
                        data = self.request.recv(1024).strip()
                        if not data:
                            break
                        bus.receive_message(data)
                        self.logger.debug("Sending SuccessfulResponse")
                        self.request.sendall(pickle.dumps(SuccessfulResponse()))
                    except Exception as e:
                        self.logger.debug("Sending FailedResponse")
                        self.request.sendall(pickle.dumps(FailedResponse(e)))
                self.logger.debug("RequestHandler stopped")

        return RequestHandler
