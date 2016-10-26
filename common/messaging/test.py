import unittest
from .message_bus import HostMessageBus, ClientMessageBus
from .messages import *


class TestMessageBus(unittest.TestCase):
    def setUp(self):
        self.host = InstrumentedHostMessageBus("host")
        self.clients = []
        for num in range(0, 4):
            self.clients.append(InstrumentedClientMessageBus("client%d" % num))

    def tearDown(self):
        self.host.stop()
        for client in self.clients:
            client.stop()
        self.clients = []
        self.host = None

    def test_initialize(self):
        # for connection initiation and request sending, a request and response are received by each bus.
        data_per_initiation = 2

        # host won't receive any data until a client connects
        self.assertEquals(self.host.num_received(), 0)
        self.host.start()
        self.assertEquals(self.host.num_received(), 0)

        # now connect to host - should have no data received until after the start method.
        # after the connect method, the host should see two more transactions, and each client should see
        # only two transactions.
        # however, because the client initiates the connection, validating that the host has received all data
        # will introduce a race condition between the host's part of the handshake and the assert.
        # so we'll only validate the client side of things here.  we still keep track of the host's data, and use it
        # in later asserts.
        host_transactions = 0
        client_transactions = dict((client, 0) for client in self.clients)
        for client in self.clients:
            self.assertEquals(client.num_received(), client_transactions[client])
            client.start(self.host.listener_address)
            host_transactions += data_per_initiation
            client_transactions[client] += data_per_initiation
            self.assertEquals(client.num_received(), client_transactions[client])

        data_per_request = 1

        # now that everyone is connected, let's have the host send a message to the clients
        # the host should receive a response from each client, and each client will receive one request
        # from the host
        self.host.send(PrintRequest("Host says hi."))
        host_transactions += (data_per_request * len(self.clients))
        self.assertEquals(self.host.num_received(), host_transactions)
        for client in self.clients:
            client_transactions[client] += data_per_request
            self.assertEquals(client.num_received(), client_transactions[client])

        # now, have each client send a request back to the host
        # the host should receive a request from each client
        # and each client should receive a response from the host
        for num in range(0, len(self.clients)):
            client = self.clients[num]
            client.send(PrintRequest("Client %d says hi." % num))
            client_transactions[client] += data_per_request
            host_transactions += data_per_request
            self.assertEquals(self.host.num_received(), host_transactions)
            self.assertEquals(client.num_received(), client_transactions[client])

        # at this point, we know that the host and client can create themselves, start themselves and then
        # communicate with one another.

class InstrumentedClientMessageBus(ClientMessageBus):
    def __init__(self, owner_id):
        super().__init__(owner_id, request_callback=self.collect)
        self.received_data = []

    def collect(self, data):
        self.received_data.append(data)

    def num_received(self):
        return len(self.received_data)


class InstrumentedHostMessageBus(HostMessageBus):
    def __init__(self, owner_id):
        super().__init__(owner_id, request_callback=self.collect)
        self.received_data = []

    def collect(self, data):
        self.received_data.append(data)

    def num_received(self):
        return len(self.received_data)
