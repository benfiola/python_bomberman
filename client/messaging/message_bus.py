import threading
import socket
import pickle
from .messages import *


class MessageBus(object):
    def __init__(self, owner_id, request_callback=None):
        """
        A message bus facilitates communication between two different machines.

        Currently has a queue for sending messages, and a queue for receiving messages.

        When initializing a connection, will first establish the connection and then send an 'IdentifyRequest' that will
        inform the remote MessageBus to tag this socket address and port with the UUID of the parent class.

        :param owner_id: the UUID of the class that spawned this - connections are tagged by UUID.
        :param request_callback: callback for further request processing - keeps implementation details out of the bus.
        """
        self.request_callback = request_callback
        self.owner_id = owner_id
        self.connections_by_id = {}
        self.connections_by_target_address = {}
        self.shutting_down = False
        self.send_queue_lock = threading.Lock()
        self.send_queue = []
        self.send_queue_thread = threading.Thread(name="request-sender-thread", target=self._process_requests_to_send)
        self.request_queue_lock = threading.Lock()
        self.request_queue = []
        self.request_queue_thread = threading.Thread(name="request-processor-thread", target=self._process_received_requests)

    def start(self):
        """
        Starts the threads that manage both the send and receive queues of the bus.
        :return:
        """
        self.send_queue_thread.start()
        self.request_queue_thread.start()

    def send(self, message):
        """
        Sends a message to connected clients (via broadcast).
        :param message: Any message that is pickleable.
        :return:
        """
        self._add_request_to_send(message)

    def stop(self):
        """
        Will shut down the bus - closing all open connections, and stopping the child threads.
        :return:
        """
        self.shutting_down = True
        self._close_connections()
        self.request_queue_thread.join()
        self.send_queue_thread.join()

    def _new_connection(self, target_address=None, target_socket=None):
        """
        Creates a connection object using a pre-created socket or a specific target address.
        Will subsequently send a IdentifyRequest to the target to inform the remote machine of this machine's unique ID.
        :param target_address: specifies a target to connect a new socket to
        :param target_socket: use this pre-existing socket
        :return: a Connection object.
        """
        if target_socket is not None:
            connection = Connection(request_callback=self._add_received_request, target_socket=target_socket)
        else:
            connection = Connection(request_callback=self._add_received_request, target_address=target_address)
        self.connections_by_target_address[connection.target_address] = connection
        connection.send(IdentifyRequest(self.owner_id, connection.source_address))
        return connection

    def _identify_connection(self, request):
        """
        Connects a socket's host and port number to a particular UUID.
        :param request: The received IdentifyRequest
        :return:
        """
        if request.target_address not in self.connections_by_target_address:
            raise ClientNotFoundException(client_target_address=request.target_address)

        connection = self.connections_by_target_address[request.target_address]
        connection.id = request.client_id
        self.connections_by_id[connection.id] = connection
        print("Identified %s:%d as %s" % (connection.target_address[0], connection.target_address[1], connection.id))

    def _close_connections(self):
        """
        Closes all connections that this bus knows of, and resets the connection maps.
        :return:
        """
        for connection in self.connections_by_target_address.values():
            connection.close()
        self.connections_by_target_address = {}
        self.connections_by_id = {}

    def _requests_to_process(self):
        """
        Fetches the current snapshot of queued requests to process, resets the queue.
        :return:
        """
        with self.request_queue_lock:
            messages = list(self.request_queue)
            self.request_queue = []
            return messages

    def _add_received_request(self, request):
        """
        Will add newly fetched request data to our processing queue.
        :param request: Any type of BaseMessage.
        :return:
        """
        with self.request_queue_lock:
            self.request_queue.append(request)

    def _process_received_requests(self):
        """
        This will process any requests that deal with the MessageBus directly, then passing these requests to a callback
        for further processing.
        :return:
        """
        while not self.shutting_down:
            requests = self._requests_to_process()
            for request in requests:
                if isinstance(request, IdentifyRequest):
                    self._identify_connection(request)
                if isinstance(request, PrintRequest):
                    print("Received print message: %s" % request.message)
                if self.request_callback is not None:
                    self.request_callback(request)

    def _requests_to_send(self):
        """
        Retrieves a current snapshot of messages needing to be sent, and then resets the queue.
        :return:
        """
        with self.send_queue_lock:
            to_return = list(self.send_queue)
            self.send_queue = []
            return to_return

    def _add_request_to_send(self, request):
        """
        Adds a new request to be broadcasted to connected and identified clients.
        :param request:
        :return:
        """
        with self.send_queue_lock:
            self.send_queue.append(request)

    def _process_requests_to_send(self):
        """
        Processes existing messages in our queue, sending them through each of our connections we know of.

        Currently, the Connection object itself has a queue for sending messages, so this really adds this message
        individually to each connection's queue.  We do this so that we have more fine-grained control over the
        sending of messages on a per-connection level.
        :return:
        """
        while not self.shutting_down:
            messages = self._requests_to_send()
            for message in messages:
                for connection in self.connections_by_id.values():
                    connection.send(message)


class ClientMessageBus(MessageBus):

    def __init__(self, owner_id, host_address, request_callback=None):
        """
        A Client message bus has a target host in mind when first created.  Then, it simply connects to this host
        when the start method is called
        """
        super().__init__(owner_id, request_callback)
        self.host_address = host_address

    def start(self):
        super().start()
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
        self.listener_socket = None
        self.listener_address = (socket.gethostname(), 40000)
        self.listener_thread = None

    def start(self):
        super().start()
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind(('', self.listener_address[1]))
        self.listener_socket.listen()
        self.listener_thread = threading.Thread(name="host-listener-thread", target=self._listen)
        self.listener_thread.start()

    def stop(self):
        super().stop()
        # Since the accept method is blocking - we need to establish a bogus connection to ourselves to unblock
        # the method call.  Since the superclass' call to stop() will set the shutting_down flag, this will effectively
        # kill the listene r thread.
        close_listener_target = ('localhost', self.listener_address[1])
        close_listener_connection = self._new_connection(target_address=close_listener_target)
        close_listener_connection.close()
        try:
            # However, for reasons that escape me, the listener_socket doesn't shutdown nicely on Windows, though calls
            # to close it result in it being closed - so we wrap it in an Exception here.
            self.listener_socket.shutdown(socket.SHUT_RDWR)
        except OSError as e:
            # If this fails, there's nothing we can do.
            pass
        self.listener_socket.close()
        self.listener_thread.join()

    def _listen(self):
        while not self.shutting_down:
            (client_socket, client_address) = self.listener_socket.accept()
            self._new_connection(target_socket=client_socket)
        print("listener stopped")


class Connection(object):
    def __init__(self, request_callback=None, target_address=None, target_socket=None):
        """
        A connection is a wrapper over the typical socket objects that dictate machine to machine communication.

        Unless a target_socket is provided, it will create a new socket with the passed-in target_address.

        Since I'm not really wanting to implement non-blocking sockets here, I've instead given sockets a very short
        timeout.

        The thread itself is managed on its own thread, called the 'connection_thread'.

        Inside this thread, oddly enough, both sending and receiving happens.  The only thing that needs queueing
        is messages that we plan to send - the idea is that the request_callback will bubble up received data
        somewhere for better processing - a Connection has no context or concept of what to do with the data it
        receives, so it makes no sense for it to hold any received data.

        :param request_callback: The callback to pass requests up the chain - usually belongs to the message bus.
        :param target_address: The address to connect a new socket to.
        :param target_socket: The socket to use in lieu of creating a new socket.
        """
        self.id = None
        self.shutting_down = False
        self.request_callback = request_callback
        self.send_queue = []
        self.send_queue_lock = threading.Lock()

        if target_socket is not None:
            self.socket = target_socket
        elif target_address is not None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(target_address)
        self.socket.settimeout(0.1)
        self.source_address = self.socket.getsockname()
        self.target_address = self.socket.getpeername()

        self.thread = threading.Thread(name="connection-thread", target=self._handle)
        self.thread.start()

    def send(self, message):
        with self.send_queue_lock:
            self.send_queue.append(message)

    def close(self):
        self.shutting_down = True
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.thread.join()

    def _messages_to_send(self):
        with self.send_queue_lock:
            to_return = list(self.send_queue)
            self.send_queue = []
            return to_return

    def _socket_send(self, message):
        """
        Sends a Python object message over socket using pickle!

        :param message: A pickleable message.
        :return:
        """
        if not self.shutting_down:
            self.socket.sendall(pickle.dumps(message))

    def _socket_receive(self, size=32768):
        """
        Receives a Python object message over socket, using pickle to deserialize.
        :param size: Maximum number of bytes to read over socket.
        :return:
        """
        if not self.shutting_down:
            try:
                data = self.socket.recv(size).strip()

                # If data is None, this means that the socket was closed
                if not data:
                    return SocketClosed()
                return pickle.loads(data)
            # Since we're setting a timeout for recv, if this exception gets thrown, the recv call timedout.
            except socket.timeout:
                return SocketReceiveTimeout()
            # If we get an OSError, odds are this socket is closed.
            except OSError:
                return SocketClosed()
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
        if isinstance(data, BaseRequest):
            print("Received request %s" % data.__class__.__name__)
            if self.request_callback is not None:
                self.request_callback(data)
                self._socket_send(RequestSuccess())

    def _handle(self):
        while not self.shutting_down:
            messages_to_send = self._messages_to_send()
            for message in messages_to_send:
                print("sending message %s" % str(message))
                self._socket_send(message)
                data = self._socket_receive()

                # This really serves to stop sending activity until we receive acknowledgement that what we've sent
                # has been received.
                while not isinstance(data, BaseResponse) and not self.shutting_down:
                    if isinstance(data, BaseRequest):
                        print("received %s in response loop" % data.__class__.__name__)
                    self._process_data(data)
                    data = self._socket_receive()

            # If we're not sending anything, we're just collecting socket messages one at a time and processing them.
            data = self._socket_receive()
            if isinstance(data, BaseResponse):
                print("received %s in request loop" % data.__class__.__name__)
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
