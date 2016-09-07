import socketserver, socket, threading, pickle, logging
from .messages import *
from common.logging import get_logger


class MessageBus(object):
    def __init__(self, response_callback):
        self.shutting_down = False
        self.logger = get_logger(self)
        self.response_callback = response_callback

    def _close_socket(self, s):
        if s is not None:
            try:
                self.logger.debug("Closing socket %s" % str(s.getpeername()))
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            except OSError as e:
                self.logger.debug("OSError when closing socket - continuing")

    def shut_down(self):
        self.logger.debug("Shutting down message bus")
        self.shutting_down = True

    def _send_message(self, s, data):
        if s is not None:
            self.logger.debug("Sending message %s" % (str(data)))
            s.sendall(pickle.dumps(data))

    def send_successful_response(self, s):
        if s is not None:
            self.logger.debug("Sending SuccessfulResponse")
            s.sendall(pickle.dumps(SuccessfulResponse()))

    def send_failed_response(self, s, e):
        if s is not None:
            self.logger.debug("Sending FailedResponse")
            s.sendall(pickle.dumps(FailedResponse(e)))

    def handle_message(self, s):
        if s is not None:
            try:
                data = s.recv(32768).strip()
                if not data:
                    return None
                message = pickle.loads(data)
                self.logger.debug("Received message %s" % (str(message)))
                self.response_callback(message)
                return message
            except OSError as e:
                self.logger.error("OSError while receiving data - continuing")
            except Exception as e:
                self.logger.exception(e)
        return None
