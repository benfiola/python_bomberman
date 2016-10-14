import socketserver, socket, threading, pickle, logging
from common.messaging import *
from common.logging import get_logger


class ClientMessageBus(MessageBus):
    def __init__(self, response_callback):
        super().__init__(response_callback)
        self.socket = None
        self.receive_thread = None

    def shut_down(self):
        super().shut_down()
        self._close_socket(self.socket)
        self.socket = None
        self.receive_thread.join()
        self.receive_thread = None

    def connect(self, target):
        if self.socket is not None:
            self._close_socket(self.socket)
            self.socket = None
        self.socket = self._create_socket(target)
        self.receive_thread = threading.Thread(name="Client-SocketReceive", target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self, data):
        self._send_message(self.socket, data)

    def receive_messages(self):
        while not self.shutting_down:
            processed_message = self.handle_message(self.socket)
            if processed_message is None:
                break
        self._close_socket(self.socket)
