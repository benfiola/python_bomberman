import unittest
import time
from .message_bus import HostMessageBus, ClientMessageBus
from .messages import *


class TestMessageBus(unittest.TestCase):
    def setUp(self):
        self.host = HostMessageBus("host")
        self.client = ClientMessageBus("client1", self.host.listener_address)

    def tearDown(self):
        self.host.stop()
        self.client.stop()

    def test_initialize(self):
        self.host.start()
        time.sleep(1)
        self.client.start()
        time.sleep(1)
        self.host.send(PrintRequest("Host says hi."))
        time.sleep(1)
        self.client.send(PrintRequest("Client says hi."))
        time.sleep(1)

