import threading
import socket
import select
import pickle
import queue
from .messages import *
from ..app_logging import create_logger


class MessageBus(object):
    def __init__(self, owner_id, request_callback=None):
        """
        A message bus facilitates communication between two different machines.

        A messsage bus has a map of connections that belong to the bus.  Each connection has its own queue
        for sending and receiving messages.

        When initializing a connection, will first establish the connection and then send an 'IdentifyRequest' that will
        inform the remote MessageBus to tag this socket address and port with the UUID of the parent class.

        :param owner_id: the UUID of the class that spawned this - connections are tagged by UUID.
        :param request_callback: callback for further request processing - keeps implementation details out of the bus.
        """
        self.logger = create_logger("message-bus")
        self.request_callback = request_callback
        self.owner_id = owner_id
        self.connections_lock = threading.Lock()
        self.connections_by_id = {}
        self.connections_by_target_address = {}
        self.connection_identification_locks = {}
        self.blocking_requests_lock = threading.Lock()
        self.blocking_requests = {}
        self.shutting_down = False

    def start(self, *args, **kwargs):
        """
        Start the message bus.
        """
        pass

    def send(self, message, target_address=None, blocking=True):
        """
        Sends a message to connected clients (via broadcast).
        :param message: Any message that is pickleable.
        :param target_address: If we're trying to communicate with a non-identified connection, we can specify a target
            address instead.
        :param blocking: Allows the function to block until all responses are received.
        :return:
        """
        with self.connections_lock:
            connections = self.connections_by_id.values()
            if target_address and target_address in self.connections_by_target_address:
                connections = [self.connections_by_target_address[target_address]]
            elif target_address:
                raise ClientNotFoundException(client_target_address=target_address)

        if blocking:
            with self.blocking_requests_lock:
                self.blocking_requests[message.id] = BlockingRequest(connections)

        for connection in connections:
            connection.send(message)

        if blocking:
            self.blocking_requests[message.id].wait()

    def stop(self):
        """
        Will shut down the bus - closing all open connections, and stopping the child threads.
        :return:
        """
        self.shutting_down = True
        self._close_connections()

    def _new_connection(self, target_address=None, target_socket=None, blocking=True):
        """
        Creates a connection object using a pre-created socket or a specific target address.
        Will subsequently send a IdentifyRequest to the target to inform the remote machine of this machine's unique ID.
        :param target_address: specifies a target to connect a new socket to
        :param target_socket: use this pre-existing socket
        :return: a Connection object.
        """
        if target_socket:
            connection = Connection(owner_name=self.owner_id, request_callback=self._process_data, target_socket=target_socket)
        else:
            connection = Connection(owner_name=self.owner_id, request_callback=self._process_data, target_address=target_address)

        remote_identification_lock = threading.Event()

        with self.connections_lock:
            self.connection_identification_locks[connection.target_address] = remote_identification_lock
            self.connections_by_target_address[connection.target_address] = connection
        self.logger.debug("Accepted connection with %s" % str(connection.target_address))

        connection.start()
        self.send(IdentifyRequest(self.owner_id, connection.source_address), target_address=connection.target_address, blocking=blocking)
        remote_identification_lock.wait()
        self.connection_identification_locks.pop(connection.target_address)
        return connection

    def _identify_connection(self, request):
        """
        Identifies a connection as belonging to a particular UUID.
        :param request: The received IdentifyRequest
        :return:
        """
        if request.target_address not in self.connections_by_target_address:
            raise ClientNotFoundException(client_target_address=request.target_address)

        with self.connections_lock:
            connection = self.connections_by_target_address[request.target_address]
            connection.id = request.client_id
            self.connections_by_id[connection.id] = connection
            self.connection_identification_locks[request.target_address].set()
        self.logger.debug("Identified %s:%d as %s" % (connection.target_address[0], connection.target_address[1], connection.id))

    def _close_connections(self):
        """
        Unblocks all blocking connections, closes all connections that this bus knows of, and resets the connection maps.
        :return:
        """
        with self.blocking_requests_lock:
            for blocking_request in self.blocking_requests.values():
                blocking_request.notify()

        with self.connections_lock:
            for connection in self.connections_by_target_address.values():
                connection.close()
            self.connections_by_target_address = {}
            self.connections_by_id = {}

    def _process_data(self, data, connection):
        """
        Process a single request received from a connection.
        :return:
        """
        if self.request_callback is not None:
            self.request_callback(data)
        if isinstance(data, RemoteSocketClosed):
            self.logger.info("Remote socket closed %s" % str(connection.target_address))
            with self.blocking_requests_lock:
                for blocking_request in self.blocking_requests.values():
                    blocking_request.notify(data.target_address)
        if isinstance(data, IdentifyRequest):
            self._identify_connection(data)
        if isinstance(data, BaseResponse):
            if isinstance(data, RequestFail):
                self.logger.error("Request failed from %s : %s" % (str(connection.target_address), str(data.message)))
            with self.blocking_requests_lock:
                if data.request_id in self.blocking_requests:
                    blocking_request = self.blocking_requests[data.request_id]
                    blocking_request.notify(connection.target_address)
        if isinstance(data, PrintRequest):
            self.logger.info("Received print message: %s" % data.message)


class ClientMessageBus(MessageBus):

    def __init__(self, owner_id, request_callback=None):
        """
        A Client message bus has a target host in mind when first created.  Then, it simply connects to this host
        when the start method is called
        """
        super().__init__(owner_id, request_callback)
        self.host_address = None

    def start(self, host_address):
        super().start()
        self.host_address = host_address
        self._new_connection(target_address=self.host_address)

    def stop(self):
        super().stop()


class HostMessageBus(MessageBus):
    def __init__(self, owner_id, request_callback=None):
        """
        A Host message bus is a standard message bus with an additional socket used to listen for new connections.

        When a new connection is accepted, a connection is spun off with the client_socket information.
        """
        super().__init__(owner_id, request_callback)
        self.listener_address = (socket.gethostname(), 40000)
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener_thread = WorkerThread(name="host-listener-thread", target=self._listen)

    def start(self):
        super().start()
        self.listener_socket.bind(('', self.listener_address[1]))
        self.listener_socket.listen()
        self.listener_thread.start()

    def stop(self):
        super().stop()

        try:
            self.listener_socket.shutdown(socket.SHUT_WR)
        except OSError as e:
            if e.errno == 57 or e.errno == 10057:
                pass
            else:
                raise e
        self.listener_socket.close()
        self.listener_thread.join()

    def _can_accept(self):
        try:
            inputs, _, closed = select.select([self.listener_socket], [], [self.listener_socket], 0.1)
        except OSError:
            inputs = []
            closed = [self.listener_socket]
        if len(closed) > 0:
            self.shutting_down = True
        return len(inputs) > 0 and not self.shutting_down

    def _listen(self, startup_lock):
        startup_lock.set()

        while not self.shutting_down:
            if self._can_accept():
                (client_socket, client_address) = self.listener_socket.accept()
                self._new_connection(target_socket=client_socket)


class Connection(object):
    def __init__(self, owner_name=None, request_callback=None, target_address=None, target_socket=None):
        """
        A connection is a wrapper over the typical socket objects that dictate machine to machine communication.

        Unless a target_socket is provided, it will create a new socket with the passed-in target_address.

        :param request_callback: The callback to pass requests up the chain - usually belongs to the message bus.
        :param target_address: The address to connect a new socket to.
        :param target_socket: The socket to use in lieu of creating a new socket.
        """
        self.logger = create_logger("connection")
        self.id = None
        self.shutting_down = False
        self.data_process_callback = request_callback

        self.send_queue = queue.Queue()
        self.send_thread = WorkerThread(name="connection_send_thread", target=self._handle_send)
        self.receive_thread = WorkerThread(name="connection_receive_thread", target=self._handle_receive)

        if target_socket is not None:
            self.socket = target_socket
        elif target_address is not None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(target_address)

        self.source_address = self.socket.getsockname()
        self.target_address = self.socket.getpeername()
        self.owner_name = owner_name

    def start(self):
        self.send_thread.start()
        self.receive_thread.start()

    def send(self, message):
        self.send_queue.put(message)

    def close(self):
        self.shutting_down = True
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.socket.close()
        self.send_thread.join()
        self.receive_thread.join()

    def _pop_message(self):
        try:
            to_return = self.send_queue.get_nowait()
            return to_return
        except queue.Empty:
            return None

    def _socket_send(self, message):
        """
        Send two messages - one notifying the recipient of the payload, and the other containing the payload.

        :param message: A pickleable message.
        :return:
        """
        if not self.shutting_down:
            try:
                pickled_message = pickle.dumps(message)
                incoming_request = pickle.dumps(IncomingRequest(len(pickled_message)))
                self.socket.sendall(incoming_request)
                self.socket.sendall(pickled_message)
            except OSError as e:
                pass

    def _can_receive(self):
        try:
            inputs, _, closed = select.select([self.socket], [], [self.socket], 0.1)
        except OSError:
            inputs = []
            closed = [self.socket]
        if len(closed) > 0:
            self.shutting_down = True
        return len(inputs) > 0 and not self.shutting_down

    def _can_write(self):
        try:
            _, outputs, closed = select.select([], [self.socket], [self.socket], 0.1)
        except OSError:
            closed = [self.socket]
            outputs = []
        if len(closed) > 0:
            self.shutting_down = True
        return len(outputs) > 0 and not self.shutting_down

    def _socket_receive(self, size=4096):
        """
        Receives a Python object message over socket, using pickle to deserialize.
        :param size: Maximum number of bytes to read over socket.
        :return:
        """
        if not self.shutting_down:
            try:
                data = self.socket.recv(size)

                # If data is None, this means that the socket was closed
                if not data:
                    return RemoteSocketClosed(self.target_address)

                data = pickle.loads(data)
                return data
            except OSError as e:
                if e.errno == 10054:
                    return RemoteSocketClosed(self.target_address)
                else:
                    self.logger.error(e)
                    return RemoteSocketClosed(self.target_address)
        # Finally, if we're shutting down, there's no point in reading - just return a SocketClosed object
        return RemoteSocketClosed(self.target_address)

    def _process_data(self, data):
        """
        With the data we've received over socket, we now process it.

        Generally, we handle SocketClosed data directly.  We process responses and requests above us,
        and return responses for requests we've received.
        :param data: A python object representing data sent over socket.
        :return:
        """
        response = None
        if self.data_process_callback is not None:
            try:
                self.data_process_callback(data, self)
                if isinstance(data, BaseRequest):
                    response = RequestSuccess(data.id)
            except Exception as e:
                if isinstance(data, BaseRequest):
                    response = RequestFail(data.id, str(e))
        if isinstance(data, RemoteSocketClosed):
            self.shutting_down = True
        if response:
            self.send(response)

    def _handle_send(self, start_lock):
        start_lock.set()
        while not self.shutting_down:
            if self._can_write():
                msg = self._pop_message()
                if msg is not None:
                    self._socket_send(msg)

    def _handle_receive(self, start_lock):
        incoming_request_size = 123
        recv_size = incoming_request_size

        start_lock.set()
        while not self.shutting_down:
            if self._can_receive():
                data = self._socket_receive(size=recv_size)
                if isinstance(data, IncomingRequest):
                    recv_size = data.size
                else:
                    self._process_data(data)
                    recv_size = incoming_request_size


class ConnectionException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ClientNotFoundException(ConnectionException):
    def __init__(self, client_id=None, client_target_address=None):
        message = None
        if client_id is not None:
            message = "Client %s not found." % client_id
        elif client_target_address is not None:
            message = "Client %s:%d not found." % client_target_address
        super().__init__(message)


class BlockingRequest(object):
    """
    Container to manage blocking requests.
    Holds a lock as well as a list of connections that a request is being sent to.

    Upon receipt of a response from these connections OR
    if the socket used in the connetion is closed, will
    check upon pending connection responses and unblock as necessary.
    """
    def __init__(self, connections):
        self.event = threading.Event()
        self.connections = {connection.target_address for connection in connections}

    def wait(self):
        if len(self.connections) > 0:
            self.event.wait()

    def notify(self, target_address=None):
        if target_address is not None:
            if target_address in self.connections:
                self.connections.remove(target_address)
                if len(self.connections) == 0:
                    self.event.set()
        else:
            self.connections = {}
            self.event.set()


class WorkerThread(threading.Thread):
    """
    A worker thread is generally a routine that runs on a separate thread whose target function generally
    just polls within a while loop for events until a certain state causes the loop to exit.

    I've found that generally, however, we want to block until the thread actually starts polling and rather
    than store locks everywhere, we can just wrap this functionality within a subclass of a Thread, and mandate
    that all targeted routines of a WorkerThread properly set the threading.Event when it has begun polling.
    """
    def __init__(self, *args, **kwargs):
        self.start_lock = threading.Event()
        args = ()
        if "args" in kwargs:
            args = kwargs["args"]
        kwargs["args"] = args + (self.start_lock, )
        super().__init__(*args, **kwargs)

    def start(self):
        super().start()
        self.start_lock.wait()
