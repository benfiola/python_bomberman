import socketserver, socket, threading, pickle, logging
from .messages import *
from common.logging import get_logger


class MessageBus(object):
    def __init__(self, source, response_callback):
        self.shutting_down = False
        self.logger = get_logger(self)
        self.source = source
        self.response_callback = response_callback
        self.sockets = {}
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer(self.source, self.generate_handler())
        self.server_thread = threading.Thread(name=self.get_thread_name(), target=self.server.serve_forever)
        self.server_thread.start()

    def close_socket(self, client):
        if client in self.sockets:
            self.logger.debug("Closing message bus socket to %s" % str(client))
            try:
                self.sockets[client].shutdown(socket.SHUT_RDWR)
                self.sockets[client].close()
            except OSError as e:
                self.logger.error("OSError when closing socket - continuing")
            self.sockets.pop(client, None)

    def shut_down(self):
        self.logger.debug("Shutting down message bus")
        clients = list(self.sockets.keys())
        for client in clients:
            self.close_socket(client)
        self.shutting_down = True
        self.server.shutdown()
        self.server_thread.join()

    def get_thread_name(self):
        import inspect
        stack = inspect.stack()
        calling_obj = stack[2][0].f_locals["self"]
        return "%s-MessageBus-SocketServer" % str(calling_obj)

    def connect(self, target):
        if target not in self.sockets:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            new_socket.connect(target)
            self.sockets[target] = new_socket

    def send_message(self, data):
        self.logger.debug("Sending message %s" % (str(data)))
        for client_socket in self.sockets.values():
            # send data
            client_socket.sendall(pickle.dumps(data))
            # receive response
            r_data = client_socket.recv(1024).strip()
            response = pickle.loads(r_data)
            self.logger.debug("Receiving response %s" % (str(response)))
            if isinstance(response, FailedResponse):
                if isinstance(response.data.error, Exception):
                    raise response.data.error
                if isinstance(response.data.error, str):
                    raise Exception(response.data.error)

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
                        data = self.request.recv(32768).strip()
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
