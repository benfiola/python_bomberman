import threading
import socket
import select
import pickle
import queue
import sys
from uuid import uuid4 as generate_uuid
from .messages import *
from ..app_logging import create_logger


class MessageBus(object):
    def __init__(self, bus_uuid, request_callback):
        """
        A message bus facilitates communication between two different machines.

        :param uuid: the UUID of the class that spawned this - connections are tagged by UUID.
        :param request_callback: a callback to process messages outside of the message bus.
        """
        self.logger = create_logger("message-bus")
        self.request_callback = request_callback
        self.uuid = bus_uuid

        self.connections_lock = threading.Lock()
        self.connections_by_id = {}
        self.connections_by_target_address = {}

        self.connection_identification_locks = {}
        self.blocking_requests_lock = threading.Lock()
        self.blocking_requests = {}
        self.shutting_down = False

        self.data_handlers = {}
        self.register_data_handler(IdentifyRequest, self._identify_connection)
        self.register_data_handler(BaseResponse, self._on_response_received)

    def start(self, *args, **kwargs):
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
        self.shutting_down = True

        with self.blocking_requests_lock:
            for blocking_request in self.blocking_requests.values():
                blocking_request.notify()
            self.blocking_requests = {}

        with self.connections_lock:
            for connection in list(self.connections_by_target_address.values()):
                connection.close()
            self.connections_by_target_address = {}
            self.connections_by_id = {}

    def data_handler(self, cls):
        """
        Decorator function for register_data_handler.

        Will register this function with all subclasses of a message type
        if a superclass is specified.

        @bus.data_handler(<message class name>)

        :param cls: Class of the Message object this method will handle.
        :return:
        """
        def decorated(func):
            self.register_data_handler(cls, func)
        return decorated

    def register_data_handler(self, cls, func):
        """
        Registers a function to handle a particular message class type.

        Will register this function with all subclasses of a message type
        if a superclass is specified.

        :param cls: Class of the Message object this method will handle.
        :param func:  Data handler function
        :return:
        """
        to_register = [cls]
        while to_register:
            curr_cls = to_register.pop()
            for subcls in curr_cls.__subclasses__():
                to_register.append(subcls)
            if curr_cls not in self.data_handlers:
                self.data_handlers[curr_cls] = []
            self.data_handlers[curr_cls].append(func)

    def _on_connection_close(self, connection):
        """
        This is called when a connection is closed unexpectedly.  When the connection detects that the socket has been
        closed remotely, it will clean itself up and then call this function so that the bus can clean up any things
        that refer to this connection.
        :param connection:
        :return:
        """
        with self.blocking_requests_lock:
            for blocking_request in self.blocking_requests.values():
                blocking_request.notify(connection.target_address)

        with self.connections_lock:
            if connection.target_address in self.connections_by_target_address:
                self.connections_by_target_address.pop(connection.target_address)
            if connection.remote_uuid in self.connections_by_id:
                self.connections_by_id.pop(connection.remote_uuid)

    def _new_connection(self, target_address=None, target_socket=None):
        """
        Creates a new Connection between this machine and a target machine.

        Connects, sends an identify request, and blocks until both machines handshake.

        :param target_address: specifies a target to connect a new socket to
        :param target_socket: use this pre-existing socket
        :return: a Connection object.
        """
        if target_socket:
            connection = Connection(self.uuid, self._process_data, self._on_connection_close, target_socket=target_socket)
        else:
            connection = Connection(self.uuid, self._process_data, self._on_connection_close, target_address=target_address)

        with self.connections_lock:
            self.connection_identification_locks[connection.target_address] = threading.Event()
            self.connections_by_target_address[connection.target_address] = connection
        self.logger.debug("Accepted connection with %s" % str(connection.target_address))

        connection.start()
        self.send(IdentifyRequest(self.uuid, connection.source_address), target_address=connection.target_address)
        self.connection_identification_locks.get(connection.target_address).wait()
        return connection

    def _identify_connection(self, request, connection):
        """
        Identifies a connection as belonging to a particular UUID.
        :param request: The received IdentifyRequest
        :return:
        """
        if connection.target_address not in self.connections_by_target_address:
            raise ClientNotFoundException(client_target_address=request.target_address)

        with self.connections_lock:
            connection.remote_uuid = request.client_id
            self.connections_by_id[connection.remote_uuid] = connection
            self.connection_identification_locks[connection.target_address].set()
        self.logger.debug("Identified %s:%d as %s" % (connection.target_address[0], connection.target_address[1], connection.remote_uuid))

    def _on_response_received(self, data, connection):
        if hasattr(data, "error"):
            self.logger.error("Request failed from %s : %s" % (str(connection.target_address), str(data.error)))
        with self.blocking_requests_lock:
            if data.request_id in self.blocking_requests:
                blocking_request = self.blocking_requests[data.request_id]
                blocking_request.notify(connection.target_address)

    def _process_data(self, data, connection):
        if self.request_callback is not None:
            self.request_callback(data)
        if data.__class__ in self.data_handlers:
            for handler in self.data_handlers[data.__class__]:
                # Internal check - if so, provide data and connection arguments.
                # If external, just provide data arguments.
                if hasattr(handler, "__self__") and isinstance(handler.__self__, MessageBus):
                    handler(data, connection)
                else:
                    handler(data)


class ClientMessageBus(MessageBus):
    def __init__(self, request_callback=None, uuid=generate_uuid()):
        """
        A Client message bus has a target host in mind when first created.  Then, it simply connects to this host
        when the start method is called
        """
        super().__init__(uuid, request_callback)
        self.host_address = None

    def start(self, host_address):
        super().start()
        self.host_address = host_address
        self._new_connection(target_address=self.host_address)

    def stop(self):
        super().stop()


class HostMessageBus(MessageBus):
    def __init__(self, request_callback, uuid=generate_uuid()):
        """
        A Host message bus is a standard message bus with an additional socket used to listen for new connections.
        """
        super().__init__(uuid, request_callback)
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
            self.listener_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.listener_socket.close()
        self.listener_thread.join()

    def _on_listener_socket_close(self):
        self.shutting_down = True

    def _listen(self, startup_lock):
        startup_lock.set()

        while not self.shutting_down:
            if SocketUtils.can_read(self.listener_socket, self._on_listener_socket_close):
                try:
                    (client_socket, client_address) = self.listener_socket.accept()
                    self._new_connection(target_socket=client_socket)
                except OSError:
                    self._on_listener_socket_close()



class Connection(object):
    def __init__(self, local_uuid, request_callback, connection_close_callback, target_address=None, target_socket=None):
        """
        A connection is a wrapper over the typical socket objects that facilitate machine to machine communication.

        Unless a target_socket is provided, it will create a new socket with the passed-in target_address.

        :param request_callback: The callback to pass requests up the chain - usually belongs to the message bus.
        :param connection_close_callback: The callback to invoke when a socket has been unexpectedly closed - requiring us to notify the bus that this connection has been closd.
        :param target_address: The address to connect a new socket to.
        :param target_socket: The socket to use in lieu of creating a new socket.
        """
        self.logger = create_logger("%s-connection" % local_uuid)
        self.remote_uuid = None
        self.shutting_down = False
        self.data_process_callback = request_callback
        self.connection_close_callback = connection_close_callback

        self.send_queue = queue.Queue()
        self.send_thread = WorkerThread(name="%s-connection_send_thread" % local_uuid, target=self._handle_send)
        self.receive_thread = WorkerThread(name="%s-connection_receive_thread" % local_uuid, target=self._handle_receive)

        if target_socket is not None:
            self.socket = target_socket
        elif target_address is not None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(target_address)

        self.source_address = self.socket.getsockname()
        self.target_address = self.socket.getpeername()
        self.local_uuid = local_uuid

    def start(self):
        self.send_thread.start()
        self.receive_thread.start()

    def send(self, message):
        self.send_queue.put(message)

    def close(self):
        """
        This method will get called when we want to close a connection in an expected fashion.
        Generally, since we're expecting this, we can assume that we're not calling this from the receive or send
        thread.  This is important because otherwise, the join calls could cause a deadlock.
        :return:
        """
        self.shutting_down = True
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.socket.close()
        self.send_thread.join()
        self.receive_thread.join()

    def _on_socket_close(self):
        """
        This will get fired when a socket has been closed unexpectedly.
        Since this can be detected in a variety of different threads, we want to close this connection (which will
        join the receive and send threads), and notify the bus that this connection is closed from an independent thread.

        Since this independent thread calls the close() method (which effectively won't return until this connection's
        threads aren't running), we can assume that when the connection_close_callback is called, that we've
        cleaned up as much as we can of this connection from within.
        :return:
        """
        self.logger.info("Socket unexpectedly closed")
        def close():
            self.close()
            self.connection_close_callback(self)
        threading.Thread(name="%s-close_connection" % self.local_uuid, target=close).start()

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
        """
        if not self.shutting_down:
            try:
                pickled_message = pickle.dumps(message)
                incoming_request = pickle.dumps(IncomingRequest(len(pickled_message)))
                self.socket.sendall(incoming_request)
                self.socket.sendall(pickled_message)
            except OSError:
                # generally, an OSError here will mean that the socket has been closed.
                self._on_socket_close()

    def _socket_receive(self, size=4096):
        """
        Receives a request/response sent over a socket.
        :param size: Number of bytes to read over socket.
        :return: A Python object or None if the connection is presently being shut down.
        """
        if not self.shutting_down:
            try:
                data = self.socket.recv(size)

                # If data is None, this means that the socket was closed
                if not data:
                    self._on_socket_close()
                else:
                    data = pickle.loads(data)
                    return data
            except OSError:
                # generally, an OSError here will mean that the socket has been closed.
                self._on_socket_close()
        # shutting down means something else is handling cleanup - nothing to do.
        return None

    def _process_data(self, data):
        response = RequestSuccess(data.id)
        try:
            self.data_process_callback(data, self)
        except Exception as e:
            self.logger.error(str(e))
            response = RequestFail(data.id, str(e))
        if data.requires_response:
            self.send(response)

    def _handle_send(self, start_lock):
        """
        This is the target of the send_thread.
        :param start_lock: An attribute of a WorkerThread, will block the creating thread until this lock is set.
        :return:
        """
        start_lock.set()
        while not self.shutting_down:
            if SocketUtils.can_write(self.socket, self._on_socket_close):
                msg = self._pop_message()
                if msg is not None:
                    self._socket_send(msg)

    def _handle_receive(self, start_lock):
        """
        This is the target of the receive_thread.
        :param start_lock: An attribute of a WorkerThread, will block the creating thread until this lock is set.
        :return:
        """
        incoming_request = IncomingRequest(sys.maxsize)
        pickled = pickle.dumps(incoming_request)
        unpickled = pickle.loads(pickled)
        incoming_request_size = len(pickle.dumps(IncomingRequest(sys.maxsize)))
        recv_size = incoming_request_size

        start_lock.set()
        while not self.shutting_down:
            if SocketUtils.can_read(self.socket, self._on_socket_close):
                data = self._socket_receive(size=recv_size)
                if data is not None:
                    if isinstance(data, IncomingRequest):
                        recv_size = data.size
                    else:
                        self._process_data(data)
                        recv_size = incoming_request_size


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


class SocketUtils(object):
    """
    This is a helper class that does basic select calls on a socket to see if it is available to write/read.
    In the event that a socket has been closed, will invoke the provided socket_close_callback function to handle
    closed sockets.
    """
    @classmethod
    def can_read(cls, sock, socket_close_callback):
        try:
            inputs, _, closed = select.select([sock], [], [sock], 0.1)
        except OSError:
            inputs = []
            closed = [sock]
        if len(closed) > 0:
            socket_close_callback()
        return len(inputs) > 0 and len(closed) == 0

    @classmethod
    def can_write(cls, sock, socket_close_callback):
        try:
            _, outputs, closed = select.select([], [sock], [sock], 0.1)
        except OSError:
            outputs = []
            closed = [sock]
        if len(closed) > 0:
            socket_close_callback()
        return len(outputs) > 0 and len(closed) == 0
