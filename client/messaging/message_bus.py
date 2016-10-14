import threading
import socket
import pickle

class MessageBus(object):
    def __init__(self):
        self.socket = None
        self.shutting_down = False
        self.send_queue = []
        self.threads = []

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def stop(self):
        pass

    def connect(self):
        """
        Connect to a target
        """
        pass

    def disconnect(self):
        """
        Disconnect from a target
        """
        pass

    def send(self, message):
        """
        Sends a message to the target
        :param message: Python object representing a message to be pickled.
        """
        pass

    def receive(self):
        """
        Receives a message from a target
        :param message:
        :return:
        """

class ClientMessageBus(MessageBus):
    """
    A client typically is just a single socket connected to a host
    """
    def __init__(self):
        super().__init__()

    def start(self):
        super().start()
        self.socket.connect(('localhost'), 40000)
        connection_thread = threading.Thread(name="client-connection-thread", target=self.handle_host)

    def handle_host(self):
        def func():
            while not self.shutting_down:





class HostMessageBus(MessageBus):
    """
    A host features a single port used to listen in on connection requests.

    When it receives a connection request, it creates a new socket and continues the conversation on that socket in
    a separate thread..
    """
    def __init__(self):
        super().__init__()

    def start(self):
        super().start()
        self.socket.bind((socket.gethostname(), 40000))
        self.socket.listen(5)
        listener_thread = threading.Thread(name="host-listener-thread", target=self.accept_connections)
        self.threads.append(listener_thread)
        listener_thread.start()

    def accept_connections(self):
        while not self.shutting_down:
            (client_socket, client_address) = self.socket.accept()
            connection_thread = threading.Thread(name="host-connection-thread-%s" % (client_address), target=self.handle_client(client_socket, client_address))
            self.threads.append(connection_thread)
            connection_thread.start()

    def handle_client(self, client_socket, client_address):
        def func():
            while not self.shutting_down:
                
                data = client_socket.recv(32768)
                if data is None:
                    break
                data = pickle.loads(data)
                print(data)
        return func




