import uuid, logging
from common.logging import get_logger
from common.messaging import MessageBus
from common.messaging.messages import *
from common.configuration import host_configuration


class Host(object):
    def __init__(self, configuration):
        self.logger = get_logger(self)
        self.configuration = configuration
        self.entity_mappings = {}
        self.board = [[]]
        self.map = None
        self.game_configuration = None
        self.entity_by_id = {}
        self.client_to_player = {}
        self.unbound_player_entities = []
        self.bus = MessageBus(self.configuration.socket_data, self.receive_message)

    def close_client_socket(self):
        self.bus.close_socket()

    def shut_down(self):
        self.bus.shut_down()

    def receive_message(self, data):
        if isinstance(data, ConnectionRequest):
            self.bus.connect(data.data)
        if isinstance(data, PrintMessage):
            print("Host received message from client : %s" % data.data)

    def send_message(self, data):
        self.bus.send_message(data)


def get_default_host_config():
    return host_configuration

