import socketserver, socket, threading, pickle, logging
from .messages import *
from common.logging import get_logger


class MessageBus(object):
    def __init__(self, response_callback):
        self.shutting_down = False
        self.logger = get_logger(self)
        self.response_callback = response_callback
        self.sock_cv = {}
        self.pending_responses = {}

    def _create_socket(self, target):
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect(target)
        self.handle_new_socket(new_socket)
        return new_socket

    def handle_new_socket(self, s):
        self.create_sock_lock(s)

    def create_sock_lock(self, s):
        self.sock_cv[s.getpeername()] = threading.Condition()

    def remove_sock_lock(self, s):
        self.sock_cv.pop(s.getpeername(), None)

    def get_sock_lock(self, s):
        return self.sock_cv[s.getpeername()]

    def _close_socket(self, s):
        if s is not None:
            try:
                self.logger.debug("Closing socket %s" % str(s.getpeername()))
                self.remove_sock_lock(s)
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
            self._receive_response(s)

    def _receive_response(self, s):
        try:
            sock_lock = self.get_sock_lock(s)
            sock_lock.acquire()
            while s not in self.pending_responses:
                sock_lock.wait()
            response = self.pending_responses[s]
            sock_lock.release()
            self.logger.debug("Received response %s" % str(response))
            if isinstance(response, FailedResponse):
                if isinstance(response.data, str):
                    raise Exception(response.data)
                else:
                    raise response.data
        except OSError as e:
            return

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
                if isinstance(message, SuccessfulResponse) or isinstance(message, FailedResponse):
                    sock_lock = self.get_sock_lock(s)
                    sock_lock.acquire()
                    self.pending_responses[s] = message
                    sock_lock.notify()
                    sock_lock.release()
                else:
                    self.response_callback(message)
                    self.send_successful_response(s)
                return message
            except OSError as e:
                self.logger.error("OSError while receiving data - continuing")
            except Exception as e:
                self.logger.exception(e)
                self.send_failed_response(s, e)
        return None
