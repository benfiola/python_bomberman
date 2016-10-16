import unittest
import time
from .message_bus import HostMessageBus, ClientMessageBus


class TestMessageBus(unittest.TestCase):
    def setUp(self):
        self.host = HostMessageBus()
        self.client_one = ClientMessageBus("client1", self.host.listener_address)
        self.client_two = ClientMessageBus("client2", self.host.listener_address)
        self.client_three = ClientMessageBus("client3", self.host.listener_address)

    def tearDown(self):
        pass

    def test_initialize(self):
        self.host.start()
        self.client_one.start()
        self.client_two.start()
        self.client_one.stop()
        self.client_three.start()
        self.client_three.stop()
        self.client_two.stop()
        self.host.stop()
