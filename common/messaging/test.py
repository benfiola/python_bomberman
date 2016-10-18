import unittest
import time
from .message_bus import HostMessageBus, ClientMessageBus
from .messages import *


class TestMessageBus(unittest.TestCase):
    def setUp(self):
        self.host = HostMessageBus("host")
        self.client_one = ClientMessageBus("client1")
        self.client_two = ClientMessageBus("client2")
        self.client_three = ClientMessageBus("client3")
        self.client_four = ClientMessageBus("client4")

    def tearDown(self):
        self.host.stop()
        self.client_one.stop()
        self.client_two.stop()
        self.client_three.stop()
        self.client_four.stop()

    def test_initialize(self):
        self.host.start()
        self.client_one.start(self.host.listener_address)
        self.client_two.start(self.host.listener_address)
        self.client_three.start(self.host.listener_address)
        self.client_four.start(self.host.listener_address)
        self.host.send(PrintRequest("Host says hi."), blocking=True)
        self.client_one.send(PrintRequest("Client one says hi."), blocking=True)
        self.client_two.send(PrintRequest("Client two says hi."), blocking=True)
        self.client_three.send(PrintRequest("Client three says hi."), blocking=True)
        self.client_four.send(PrintRequest("Client four says hi."), blocking=True)

