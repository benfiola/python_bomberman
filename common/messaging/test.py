import unittest
from . import *
from ..app_logging import create_logger


class TestMessageBus(unittest.TestCase):
    def setUp(self):
        self.logger = create_logger("message_bus_test")
        self.host = InstrumentedHostMessageBus()
        self.clients = [InstrumentedClientMessageBus(num) for num in range(0, 4)]

    def tearDown(self):
        self.logger.info("Tearing down")
        self.host.stop()
        for client in self.clients:
            client.stop()
        self.clients = []
        self.host = None

    def test_initialize(self):
        # host won't receive any data until a client connects
        self.assertEquals(self.host.num_received(), 0)
        self.host.start()
        self.assertEquals(self.host.num_received(), 0)

        # now connect to host - should have no data received until after the start method.
        # we should expect that both host and client will receive a request per interaction.
        host_transactions = 0
        client_transactions = dict((client, 0) for client in self.clients)
        for client in self.clients:
            self.logger.info("Connecting %s to host" % client.uuid)
            self.assertEquals(client.num_received(), client_transactions[client])
            client.start(self.host.listener_address)
            host_transactions += 1
            client_transactions[client] += 1
            self.assertEquals(client.num_received(), client_transactions[client])
        self.assertEquals(self.host.num_received(), host_transactions)

        # now that everyone is connected, let's have host and clients send messages to each other.
        # we'll make sure each side receives the correct number of requests.

        # start with the host broadcasting a message to all clients.
        self.host.send(PrintRequest("Host says hi."))
        self.assertEquals(self.host.num_received(), host_transactions)
        for client in self.clients:
            client_transactions[client] += 1
            self.assertEquals(client.num_received(), client_transactions[client])

        # now let's have clients send a message back to the host.
        for num in range(0, len(self.clients)):
            client = self.clients[num]
            client.send(PrintRequest("Client %d says hi." % num))
            host_transactions += 1
            self.assertEquals(self.host.num_received(), host_transactions)


class InstrumentedClientMessageBus(ClientNetworkedMessageBus):
    def __init__(self, number):
        super().__init__("client-%d" % number)
        self.received_data = []
        self.register_data_handler(BaseMessage, self.collect)
        self.register_data_handler(PrintRequest, self.print)

    def collect(self, data, connection):
        if isinstance(data, RequestFail):
            raise Exception("Request failed with message: %s" % data.error)
        elif not isinstance(data, BaseResponse):
            self.received_data.append(data)

    def num_received(self):
        return len(self.received_data)

    def print(self, data, connection):
        self.logger.info("%s received message: %s" % (self.uuid, self.data.message))


class InstrumentedHostMessageBus(HostNetworkedMessageBus):
    def __init__(self):
        super().__init__("host")
        self.received_data = []
        self.register_data_handler(BaseMessage, self.collect)
        self.register_data_handler(PrintRequest, self.print)

    def collect(self, data, connection):
        if isinstance(data, RequestFail):
            raise Exception("Request failed with message: %s" % data.error)
        elif not isinstance(data, BaseResponse):
            self.received_data.append(data)

    def num_received(self):
        return len(self.received_data)

    def print(self, data, connection):
        self.logger.info("%s received message: %s" % (self.uuid, data.message))
