import threading
import socket
import pickle
from .messages import IdentifyRequest, RequestFail, RequestSuccess


class MessageBus(object):
    def __init__(self):
        self.connections_by_id = {}
        self.connections_by_target_address = {}
        self.shutting_down = False
        self.send_queue = []

    def start(self):
        pass

    def stop(self):
        self.shutting_down = True
        self.disconnect()

    def connect(self):
        pass

    def add_connection(self, connection):
        if connection.id is not None:
            if connection.id in self.connections_by_id:
                self.disconnect(connection_id=connection.id)
            self.connections_by_id[connection.id] = connection
        self.connections_by_target_address[connection.target_address] = connection

    def identify_connection(self, connection, connection_id):
        connection.id = connection_id
        self.connections_by_id[connection.id] = connection

    def disconnect(self, connection_id=None, connection_target_address=None):
        if connection_id is not None:
            if connection_id in self.connections_by_id:
                connection = self.connections_by_id.pop(connection_id)
                self.connections_by_target_address.pop(connection.target_address)
                connection.close()
            else:
                raise ClientNotFoundException(connection_id)
        elif connection_target_address is not None:
            if connection_target_address in self.connections_by_target_address:
                connection = self.connections_by_target_address.pop(connection_target_address)
                if connection.id in self.connections_by_id:
                    self.connections_by_id.pop(connection.id)
                connection.close()
            else:
                raise ClientNotFoundException("%s:%d" % connection_target_address)
        else:
            for connection in self.connections_by_target_address.values():
                connection.close()
            self.connections_by_target_address = {}
            self.connections_by_id = {}

    def send(self, message, connection_id=None):
        if connection_id is not None:
            if connection_id in self.connections_by_id:
                self.connections_by_id[connection_id].send(message)
            else:
                raise ClientNotFoundException(connection_id)
        else:
            for connection in self.connections_by_id.values():
                connection.send(message)


class ClientMessageBus(MessageBus):
    def __init__(self, client_id, host_address):
        super().__init__()
        self.client_id = client_id
        self.host_address = host_address

    def start(self):
        super().start()
        connection = Connection("host", target_address=self.host_address)
        self.add_connection(connection)
        connection.send(IdentifyRequest(self.client_id))
        print("client started")

    def stop(self):
        print("client stopping")
        super().stop()


class HostMessageBus(MessageBus):
    def __init__(self):
        super().__init__()
        self.listener_socket = None
        self.listener_address = (socket.gethostname(), 40000)
        self.listener_thread = None

    def start(self):
        super().start()
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind(('', self.listener_address[1]))
        self.listener_socket.listen()
        self.listener_thread = threading.Thread(name="host-listener-thread", target=self.listen)
        self.listener_thread.start()
        print("host started")

    def stop(self):
        print("host stopping")
        super().stop()
        close_listener_target = ('localhost', self.listener_address[1])
        close_listener_connection = Connection("close_listener", target_address=close_listener_target)
        close_listener_connection.close()
        try:
            self.listener_socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            # If this fails, there's nothing we can do.
            pass
        self.listener_socket.close()
        self.listener_thread.join()

    def listen(self):
        while not self.shutting_down:
            (client_socket, client_address) = self.listener_socket.accept()
            print("host accepted connection from %s" % str(client_address))
            connection = Connection(client_address, target_socket=client_socket)
            self.add_connection(connection)
        print("no listening")


class Connection(object):
    def __init__(self, connection_id, target_address=None, target_socket=None):
        self.id = connection_id
        if target_socket is not None:
            self.socket = target_socket
        elif target_address is not None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(target_address)
        self.target_address = self.socket.getpeername()
        self.shutting_down = False
        self.thread = threading.Thread(name="connection-thread-%s" % str(connection_id), target=self.handle)
        self.send_queue = []
        self.thread.start()

    def send(self, message):
        self.send_queue.append(message)

    def get_messages_to_send(self):
        to_return = list(self.send_queue)
        self.send_queue = []
        return to_return

    def _send(self, message):
        if not self.shutting_down:
            self.socket.sendall(pickle.dumps(message))

    def _receive(self, size=32768):
        if not self.shutting_down:
            try:
                data = self.socket.recv(size).strip()
            except Exception as e:
                # If this fails, then something is wrong with our socket.
                data = None
            if not data:
                self.shutting_down = True
            return data
        return None

    def handle(self):
        while not self.shutting_down:
            messages_to_send = self.get_messages_to_send()
            for message in messages_to_send:
                self._send(message)
                data = self._receive()
                if not data:
                    break
                data = pickle.loads(data)
                print(data)
            data = self._receive()
            if not data:
                break
            print(data)
            data = pickle.loads(data)
            print(data)
        print("connection closed")

    def close(self):
        self.shutting_down = True
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.thread.join()


class ConnectionException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ClientNotFoundException(ConnectionException):
    def __init__(self, message):
        super().__init__(message)
