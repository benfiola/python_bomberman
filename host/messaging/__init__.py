import socketserver, socket, threading, pickle, logging
from common.messaging import *
from common.logging import get_logger


class HostMessageBus(MessageBus):
    def __init__(self, address, response_callback):
        super().__init__(response_callback)
        self.sockets = {}
        self.address = address
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        self.server = socketserver.ThreadingTCPServer(self.address, self.generate_handler())
        self.server_thread = threading.Thread(name="Host-MessageBus-SocketServer", target=self.server.serve_forever)
        self.server_thread.start()

    def close_socket(self, client):
        if client in self.sockets:
            s = self.sockets[client]
            self._close_socket(s)
            self.sockets.pop(client, None)

    def shut_down(self):
        super().shut_down()
        clients = list(self.sockets.keys())
        for client in clients:
            self.close_socket(client)
        self.server.shutdown()
        self.server_thread.join()

    def register_socket(self, s):
        self.logger.info("Registering socket %s" % str(s.getpeername()))
        self.sockets[s.getpeername()] = s

    def send_message(self, data):
        for client_socket in self.sockets.values():
            self._send_message(client_socket, data)

    def generate_handler(self):
        bus = self

        class RequestHandler(socketserver.BaseRequestHandler):
            def __init__(self, *args, **kwargs):
                self.logger = get_logger(self)
                super().__init__(*args, **kwargs)

            def handle(self):
                socket_name = self.request.getpeername()
                bus.register_socket(self.request)
                while not bus.shutting_down:
                    processed_message = bus.handle_message(self.request)
                    if processed_message is None:
                        break
                bus.close_socket(socket_name)
                self.logger.debug("RequestHandler stopped")

        return RequestHandler
