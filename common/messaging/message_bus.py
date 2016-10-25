import threading
import socket
import select
import pickle
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
        self.connections_by_id = {}
        self.connections_by_target_address = {}
        self.pending_requests_lock = threading.Lock()
        self.pending_requests = {}
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
        :param target_address: Specify target_address to send message to
        :return:
        """
        # Since the IdentifyRequest seeks to add a connection to the connections_by_ids map, there's no way
        # we can use the default 'broadcast to identified connections' behavior.  That's why we offer the ability
        # to send messages directly to target_addresses as well.
        connections = self.connections_by_id.values()
        if target_address is not None:
            if target_address in self.connections_by_target_address:
                connections = [self.connections_by_target_address[target_address]]
            else:
                exc = ClientNotFoundException(client_target_address=target_address)
                self.logger.info(str(exc))
                raise exc

        if blocking and len(connections) > 0:
            with self.pending_requests_lock:
                self.pending_requests[message.id] = (threading.Event(), len(connections))

        for connection in connections:
            connection.send(message)

        if blocking and len(connections) > 0:
            request_lock, _ = self.pending_requests[message.id]
            request_lock.wait()

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
        if target_socket is not None:
            connection = Connection(owner_name=self.owner_id, request_callback=self._process_request, target_socket=target_socket)
        else:
            connection = Connection(owner_name=self.owner_id, request_callback=self._process_request, target_address=target_address)
        self.connections_by_target_address[connection.target_address] = connection
        connection.start()
        self.logger.info("Accepted connection with %s" % str(connection.target_address))

        self.send(IdentifyRequest(self.owner_id, connection.source_address), target_address=connection.target_address, blocking=blocking)
        return connection

    def _identify_connection(self, request):
        """
        Connects a socket's host and port number to a particular UUID.
        :param request: The received IdentifyRequest
        :return:
        """
        if request.target_address not in self.connections_by_target_address:
            exc = ClientNotFoundException(client_target_address=request.target_address)
            self.logger.info(str(exc))
            raise exc
        connection = self.connections_by_target_address[request.target_address]
        connection.id = request.client_id
        self.connections_by_id[connection.id] = connection
        self.logger.debug("Identified %s:%d as %s" % (connection.target_address[0], connection.target_address[1], connection.id))

    def _close_connections(self):
        """
        Closes all connections that this bus knows of, and resets the connection maps.
        :return:
        """
        for connection in self.connections_by_target_address.values():
            connection.close()
        self.connections_by_target_address = {}
        self.connections_by_id = {}

    def _process_request(self, request):
        """
        Process a single request received from a connection.
        :return:
        """
        if isinstance(request, IdentifyRequest):
            self._identify_connection(request)
        if isinstance(request, BaseResponse):
            with self.pending_requests_lock:
                (lock, num_waiting) = self.pending_requests[request.request_id]
                num_waiting -= 1
                if num_waiting == 0:
                    self.pending_requests.pop(request.request_id)
                    lock.set()
                else:
                    self.pending_requests[request.request_id] = (lock, num_waiting)
        if isinstance(request, PrintRequest):
            self.logger.info("Received print message: %s" % request.message)
        if self.request_callback is not None:
            self.request_callback(request)


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
        self.listener_thread = threading.Thread(name="host-listener-thread", target=self._listen)
        self.listener_thread_startup_event = threading.Event()

    def start(self):
        super().start()
        self.listener_socket.bind(('', self.listener_address[1]))
        self.listener_socket.listen()
        self.listener_thread.start()
        self.listener_thread_startup_event.wait()

    def stop(self):
        super().stop()
        # Since the accept method is blocking - we need to establish a bogus connection to ourselves to unblock
        # the method call.  Since the superclass' call to stop() will set the shutting_down flag, this will effectively
        # kill the listene r thread.
        close_listener_target = ('localhost', self.listener_address[1])
        close_listener_connection = self._new_connection(target_address=close_listener_target, blocking=False)
        close_listener_connection.close()
        try:
            # For reasons that escape me, the listener_socket doesn't shutdown.
            # Calls to close it result in it being closed - so we wrap it in an Exception here.
            self.listener_socket.shutdown(socket.SHUT_RDWR)
        except OSError as e:
            # If this fails, there's nothing we can do.
            pass
        self.listener_socket.close()
        self.listener_thread.join()

    def _listen(self):
        self.listener_thread_startup_event.set()

        while not self.shutting_down:
            (client_socket, client_address) = self.listener_socket.accept()
            if not self.shutting_down:
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
        self.request_callback = request_callback

        receive_thread_name = "connection_receive_thread"
        send_thread_name = "connection_send_thread"
        if owner_name is not None:
            receive_thread_name = "%s-connection_receive_thread" % owner_name
            send_thread_name = "%s-connection_send_thread" % owner_name

        self.send_queue = []
        self.send_queue_lock = threading.Lock()
        self.send_thread_start_event = threading.Event()
        self.send_thread = threading.Thread(name=send_thread_name, target=self._handle_send)
        self.receive_thread_start_event = threading.Event()
        self.receive_thread = threading.Thread(name=receive_thread_name, target=self._handle_receive)

        if target_socket is not None:
            self.socket = target_socket
        elif target_address is not None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(target_address)
        self.source_address = self.socket.getsockname()
        self.target_address = self.socket.getpeername()
        self.owner_name = owner_name

    def start(self):
        self.send_thread_start_event.clear()
        self.receive_thread_start_event.clear()
        self.send_thread.start()
        self.receive_thread.start()
        self.send_thread_start_event.wait()
        self.receive_thread_start_event.wait()

    def send(self, message):
        with self.send_queue_lock:
            self.send_queue.append(message)

    def close(self):
        self.shutting_down = True
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.socket.close()
        self.send_thread.join()
        self.receive_thread.join()
        self.send_thread_start_event.clear()
        self.receive_thread_start_event.clear()

    def _pop_message(self):
        with self.send_queue_lock:
            return self.send_queue.pop()

    def _has_messages(self):
        with self.send_queue_lock:
            return len(self.send_queue) > 0

    def _socket_send(self, message):
        """
        Sends a Python object message over socket using pickle!

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
                print(e)

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
                    return SocketClosed()
                data = pickle.loads(data)
                return data
            # Since we're setting a timeout for recv, if this exception gets thrown, the recv call timedout.
            except socket.timeout:
                return SocketReceiveTimeout()
            # If we get an OSError, odds are this socket is closed.
            except OSError:
                return SocketClosed()
            except Exception as e:
                self.logger.error(e)
        # Finally, if we're shutting down, there's no point in reading - just return a SocketClosed object
        return SocketClosed()

    def _process_data(self, data):
        """
        With the data we've received over socket, we now process it.

        Generally, we're only looking for SocketClosed information here - from which we use to kill our
        Connection threads.  If the data is a serviceable Request, we bubble it up via our callbacks.
        :param data: A python object representing data sent over socket.
        :return:
        """
        if isinstance(data, SocketClosed):
            self.shutting_down = True
        if isinstance(data, BaseRequest) or isinstance(data, BaseResponse):
            if self.request_callback is not None:
                self.request_callback(data)
        if isinstance(data, BaseRequest):
            self.send(RequestSuccess(data.id))

    def _handle_send(self):
        self.send_thread_start_event.set()
        while not self.shutting_down:
            if self._can_write() and self._has_messages():
                self._socket_send(self._pop_message())

    def _handle_receive(self):
        self.receive_thread_start_event.set()
        while not self.shutting_down:
            if self._can_receive():
                # receive a message
                data = self._socket_receive(size=123)
                if isinstance(data, IncomingRequest):
                    data = self._socket_receive(data.size)
                    self._process_data(data)


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
