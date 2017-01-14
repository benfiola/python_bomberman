import threading
import socket
import select
import pickle
import queue
from .messages import *
from ..app_logging import logging


class MessageBus(object):
    def __init__(self, bus_uuid):
        self.uuid = bus_uuid
        self.logger = logging.getLogger("message-bus")
        self.data_handlers = {}

    def start(self):
        pass

    def send(self, message):
        pass

    def stop(self):
        pass

    def data_handler(self, cls):
        def decorated(func):
            self.register_data_handler(cls, func)
        return decorated

    def register_data_handler(self, cls, func):
        to_register = [cls]
        while to_register:
            curr_cls = to_register.pop()
            for subcls in curr_cls.__subclasses__():
                to_register.append(subcls)
            if curr_cls not in self.data_handlers:
                self.data_handlers[curr_cls] = []
            self.data_handlers[curr_cls].append(func)


class LocalMessageBus(MessageBus):
    def __init__(self, bus_uuid):
        super().__init__(bus_uuid)

    def start(self, *args):
        super().start()

    def stop(self):
        super().stop()

    def send(self, data):
        for handler in self.data_handlers[data.__class__]:
            handler(data)


class NetworkedMessageBus(MessageBus):
    def __init__(self, bus_uuid):
        """
        A message bus facilitates communication between two networked machines.

        :param uuid: the UUID of the class that spawned this - connections are tagged by UUID.
        :param request_callback: a callback to process messages outside of the message bus.
        """
        super().__init__(bus_uuid)

        self.connection_manager = ConnectionManager(self)
        self.request_manager = RequestManager(self)
        self.shutting_down = False

        self.register_data_handler(Identify, self.connection_manager.identify)
        self.register_data_handler(BaseResponse, self.request_manager.on_response)

    def start(self, *args):
        super().start()

    def send(self, message, target_address=None, blocking=True):
        """
        Sends a message to connected clients (via broadcast).
        :param message: Any message that is pickleable.
        :param target_address: If we're trying to communicate with a non-identified connection, we can specify a target
            address instead.
        :param blocking: Allows the function to block until all responses are received.
        :return:
        """
        connections = self.connection_manager.get(target_address)
        self.request_manager.send(message, connections, blocking)

    def stop(self):
        super().stop()
        self.shutting_down = True
        connections = self.connection_manager.get()
        for connection in connections:
            self.request_manager.notify(connection)
            self.connection_manager.close(connection)

    def handle_closed_remote_socket(self, connection):
        self.request_manager.notify(connection)
        self.connection_manager.close(connection)

    def handle_data(self, data, connection):
        if data.__class__ in self.data_handlers:
            for handler in self.data_handlers[data.__class__]:
                # if it's internal, we probably care about the connection
                # if it's an external data handler, all that matters is the data argument
                # let's enforce this here.
                if hasattr(handler, '__self__') and isinstance(handler.__self__, (ConnectionManager, RequestManager, MessageBus)):
                    handler(data, connection)
                else:
                    handler(data)


class ClientNetworkedMessageBus(NetworkedMessageBus):
    def __init__(self, bus_uuid):
        """
        A Client message bus has a target host in mind when first created.  Then, it simply connects to this host
        when the start method is called
        """
        super().__init__(bus_uuid)
        self.host_address = None

    def start(self, host_address):
        super().start()
        self.host_address = host_address
        connection = self.connection_manager.open(target_address=self.host_address)
        self.request_manager.send(Identify(self.uuid, connection.source_address), connections=[connection])
        self.connection_manager.wait_until_handshake(connection)

    def stop(self):
        super().stop()
        self.logger.info("client networked message bus stopped")


class HostNetworkedMessageBus(NetworkedMessageBus):
    def __init__(self, bus_uuid, host_port):
        """
        A Host message bus is a standard message bus with an additional socket used to listen for new connections.
        """
        super().__init__(bus_uuid)
        self.listener_address = (socket.gethostname(), host_port)
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
        self.logger.info("host networked message bus stopped")

    def _on_listener_socket_close(self):
        self.shutting_down = True

    def _listen(self, startup_lock):
        startup_lock.set()

        while not self.shutting_down:
            if self.listener_socket.can_read(self._on_listener_socket_close):
                try:
                    (client_socket, client_address) = self.listener_socket.accept()
                    connection = self.connection_manager.open(target_socket=client_socket)
                    self.request_manager.send(Identify(self.uuid, connection.source_address), connections=[connection])
                    self.connection_manager.wait_until_handshake(connection)
                except OSError:
                    self._on_listener_socket_close()


class Connection(object):
    def __init__(self, bus, target_address=None, target_socket=None):
        """
        A connection is a wrapper over the typical socket objects that facilitate machine to machine communication.

        Unless a target_socket is provided, it will create a new socket with the passed-in target_address.

        :param request_callback: The callback to pass requests up the chain - usually belongs to the message bus.
        :param connection_close_callback: The callback to invoke when a socket has been unexpectedly closed - requiring us to notify the bus that this connection has been closd.
        :param target_address: The address to connect a new socket to.
        :param target_socket: The socket to use in lieu of creating a new socket.
        """
        self.logger = logging.getLogger("%s-connection" % bus.uuid)
        self.local_uuid = bus.uuid
        self.remote_uuid = None
        self.shutting_down = False
        self.data_process_callback = bus.handle_data
        self.connection_close_callback = bus.handle_closed_remote_socket

        self.send_queue = queue.Queue()
        self.send_thread = WorkerThread(name="%s-connection_send_thread" % self.local_uuid, target=self._handle_send)
        self.receive_thread = WorkerThread(name="%s-connection_receive_thread" % self.local_uuid, target=self._handle_receive)

        if target_socket is not None:
            self.socket = target_socket
        elif target_address is not None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(target_address)

        self.source_address = self.socket.getsockname()
        self.target_address = self.socket.getpeername()

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
        response = RequestSuccess(data.uuid)
        try:
            self.data_process_callback(data, self)
        except Exception as e:
            self.logger.error(str(e))
            response = RequestFail(data.uuid, str(e))
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
            if self.socket.can_write(self._on_socket_close):
                msg = self._pop_message()
                if msg is not None:
                    self._socket_send(msg)

    def _handle_receive(self, start_lock):
        """
        This is the target of the receive_thread.
        :param start_lock: An attribute of a WorkerThread, will block the creating thread until this lock is set.
        :return:
        """
        incoming_request_size = len(pickle.dumps(IncomingRequest(0)))
        recv_size = incoming_request_size

        start_lock.set()
        while not self.shutting_down:
            if self.socket.can_read(self._on_socket_close):
                data = self._socket_receive(size=recv_size)
                if data is not None:
                    if isinstance(data, IncomingRequest):
                        recv_size = data.size
                    else:
                        self._process_data(data)
                        recv_size = incoming_request_size


class Request(object):
    """
    This object contains a message and all the connections its been sent to.

    It has the ability to block until all recipients acknowledge receipt.

    Upon receipt of a response from these connections OR
    if the socket used in the connetion is closed, will
    check upon pending connection responses and unblock as necessary.
    """
    def __init__(self, message, connections, blocking):
        self.message = message
        self.event = None
        if blocking:
            self.event = threading.Event()
        self.connections = dict((connection, 1) for connection in connections)

    def send(self):
        if len(self.connections) > 0:
            for connection in self.connections.keys():
                connection.send(self.message)
            if self.event:
                self.event.wait()

    def notify(self, connection):
        if connection is None:
            self.connections = {}
        else:
            if connection in self.connections:
                self.connections.pop(connection)
        if len(self.connections) == 0 and self.event:
            self.event.set()


class RequestManager(object):
    """
    A request manager simply handles all 'requests' as issued from
    a message bus.  This way, we can keep all the request blocking behavior
    and memoization of pending requests separate from the message bus, which
    kinda cluttered the code.
    """
    def __init__(self, bus):
        self.logger = logging.getLogger("request-manager")
        self.bus = bus

        self.pending_requests_lock = threading.Lock()
        self.pending_requests = {}

    def send(self, message, connections, blocking=True):
        request = Request(message, connections, blocking)
        with self.pending_requests_lock:
            if request.message.uuid in self.pending_requests:
                raise Exception("Resending a pending request?")
            self.pending_requests[request.message.uuid] = request
            request.send()

    def notify(self, connection, request=None):
        """
        Delegates to the request's notify function, but
        will also clear the pending_requests dictionary
        if a request has no more pending connection responses.
        :param connection:
        :param request:
        :return:
        """
        if request is None:
            requests = list(self.pending_requests.values())
        else:
            requests = [request]
        for request in requests:
            request.notify(connection)
            if len(request.connections) == 0:
                self.pending_requests.pop(request.message.uuid)

    def on_response(self, data, connection):
        """
        Convenience method for plugging into the message_bus data handling
        system.
        :param data:
        :param connection:
        :return:
        """
        if data.request_id in self.pending_requests:
            request = self.pending_requests[data.request_id]
            self.notify(connection, request)


class ConnectionManager(object):
    """
    A connection manager simply handles connections between two machines.
    Anything involving memoizing connections and establishing, handshaking
    and closing a socket connection gets passed through here in an effort
    to reduce clutter in the message bus.
    """
    def __init__(self, bus):
        self.logger = logging.getLogger("connection-manager")
        self.bus = bus

        self.connections_lock = threading.Lock()
        self.connections_by_id = {}
        self.connections_by_target_address = {}

        self.connection_identification_locks = {}
        self.blocking_requests_lock = threading.Lock()
        self.blocking_requests = {}

    def open(self, **kwargs):
        """
        Creates a new Connection between this machine and a target machine.

        Connects, sends an identify request, and blocks until both machines handshake.

        :param target_address: specifies a target to connect a new socket to
        :param target_socket: use this pre-existing socket
        :return: a Connection object.
        """
        connection = Connection(self.bus, **kwargs)

        with self.connections_lock:
            self.connection_identification_locks[connection.target_address] = threading.Event()
            self.connections_by_target_address[connection.target_address] = connection
        self.logger.debug("Accepted connection with %s" % str(connection.target_address))

        connection.start()
        return connection

    def wait_until_handshake(self, connection):
        """
        When a connection is created, we need to send an
        IdentifyRequest through the RequestManager to initiate
        a handshake - however, once this is done, we want to wait
        until we've confirmed that the handshake has succeeded.
        :param connection:
        :return:
        """
        self.connection_identification_locks[connection.target_address].wait()

    def get(self, target_address=None):
        with self.connections_lock:
            if target_address is None:
                return list(self.connections_by_id.values())
            else:
                if target_address not in self.connections_by_target_address:
                    raise ClientNotFoundException(client_target_address=target_address)
                return [self.connections_by_target_address[target_address]]

    def close(self, connection):
        with self.connections_lock:
            if connection.remote_uuid in self.connections_by_id:
                self.connections_by_id.pop(connection.remote_uuid)
            if connection.target_address in self.connections_by_target_address:
                self.connections_by_target_address.pop(connection.target_address)
            if not connection.shutting_down:
                connection.close()

    def identify(self, request, connection):
        with self.connections_lock:
            connection.remote_uuid = request.client_id
            self.connections_by_id[request.uuid] = connection
            self.connection_identification_locks[connection.target_address].set()
        self.logger.debug("Identified %s:%d as %s" % (connection.target_address[0], connection.target_address[1], connection.remote_uuid))


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

# Here, I'm going to monkey patch some 'helpful' methods here onto socket.socket.
# Basically, when I work with sockets, I use these can_read
# and can_write helper methods to help determine if it's worthwhile
# to block on a read/write.  However, since I use sockets in more
# than one place, it seems 'cleaner' to patch it onto the socket object
# in lieu of subclassing (which doesn't work with accept) or writing
# a helper set of static methods that take a socket and a callback
# as an argument.
def can_read(self, socket_close_callback):
    try:
        inputs, _, closed = select.select([self], [], [self], 0.1)
    except OSError:
        inputs = []
        closed = [self]
    if len(closed) > 0:
        socket_close_callback()
    return len(inputs) > 0 and len(closed) == 0


def can_write(self, socket_close_callback):
    try:
        _, outputs, closed = select.select([], [self], [self], 0.1)
    except OSError:
        outputs = []
        closed = [self]
    if len(closed) > 0:
        socket_close_callback()
    return len(outputs) > 0 and len(closed) == 0

socket.socket.can_read = can_read
socket.socket.can_write = can_write
