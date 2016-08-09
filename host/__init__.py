from common.logging import get_logger
from common.messaging import MessageBus
from common.messaging.messages import *
from common.configuration import host_configuration
from .custom_events import *
from .game import *


class Host(object):
    def __init__(self, owner, configuration):
        self.owner = owner
        self.logger = get_logger(self)
        self.configuration = configuration
        self.game = None
        self.shutting_down = False
        self.custom_events = []
        self.bus = MessageBus(self.configuration.socket_data, self.receive_message)

    def close_client_socket(self):
        self.bus.close_socket()

    def shut_down(self):
        self.bus.shut_down()

    def push_custom_event(self, event):
        self.custom_events.append(event)

    def get_custom_events(self):
        to_return = self.custom_events
        self.custom_events = []
        return to_return

    def validate_id(self, event):
        return self.owner == event.client_id

    def receive_message(self, message):
        if isinstance(message, ConnectionRequest):
            self.push_custom_event(ClientConnectionEvent(message.data.client_id, message.data.socket_data))
        if isinstance(message, DisconnectionRequest):
            self.push_custom_event(ClientDisconnectionEvent(message.data.client_id, message.data.socket_data))
        if isinstance(message, HostShutdownMessage):
            self.push_custom_event(QuitEvent(message.data.client_id))
        if isinstance(message, InitializeGameMessage):
            self.push_custom_event(InitializeGameEvent(message.data.client_id, message.data.configuration))
        if isinstance(message, StartGameMessage):
            self.push_custom_event(StartGameEvent(message.data.client_id))
        if isinstance(message, PrintMessage):
            print("Host received message from client : %s" % message.data.message)

    def create_game(self, game_configuration):
        self.game = Game(game_configuration)

    def send_message(self, data):
        self.bus.send_message(data)

    def connect_to_client(self, client):
        self.bus.connect(client)

    def disconnect_from_client(self, client):
        self.bus.close_socket(client)

    def log_event(self, event):
        self.logger.debug("Received event %s" % str(event))

    def run(self):
        self.logger.info("Host started")
        while not self.shutting_down:
            events = self.get_custom_events()
            for event in events:
                self.log_event(event)
                allow_event_dispatch = True
                if isinstance(event, ClientValidatedEvent):
                    allow_event_dispatch = self.validate_id(event)
                if allow_event_dispatch:
                    if isinstance(event, InitializeGameEvent):
                        self.create_game(event.game_configuration)
                    if isinstance(event, StartGameEvent):
                        self.game.assign_player_to_client(event.client_id)
                    if isinstance(event, ClientConnectionEvent):
                        self.connect_to_client(event.socket_data)
                    if isinstance(event, ClientDisconnectionEvent):
                        self.disconnect_from_client(event.socket_data)
                    if isinstance(event, QuitEvent):
                        self.shutting_down = True
                        break
                else:
                    self.logger.debug("Host disallowed event %s because client_id %s does not match %s" % (str(event), str(event.client_id), str(self.owner)))
        self.shut_down()


def get_default_host_config():
    return host_configuration

