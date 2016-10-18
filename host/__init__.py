import uuid
from common.app_logging import get_logger
from .messaging import HostMessageBus
from common.messaging.messages import *
from common.configuration import host_configuration
from .custom_events import *
from .game import *


class Host(object):
    def __init__(self, owner, configuration):
        self.id = uuid.uuid4()
        self.owner = owner
        self.logger = get_logger(self)
        self.configuration = configuration
        self.game = None
        self.shutting_down = False
        self.custom_events = []
        self.bus = HostMessageBus(self.configuration.socket_data, self.receive_message)

    def shut_down(self):
        if not self.shutting_down:
            self.logger.info("Host shutting down")
            self.bus.shut_down()
            self.shutting_down = True

    def push_custom_event(self, event):
        self.custom_events.append(event)

    def get_custom_events(self):
        to_return = self.custom_events
        self.custom_events = []
        return to_return

    def validate_id(self, event):
        return self.owner == event.client_id

    def receive_message(self, message):
        if isinstance(message, ClientConnectionRequest):
            self.push_custom_event(ClientConnectionEvent(message.data.client_id, message.data.socket_data))
        if isinstance(message, ClientDisconnectionRequest):
            self.push_custom_event(ClientDisconnectionEvent(message.data.client_id, message.data.socket_data))
        if isinstance(message, HostShutdownRequest):
            self.push_custom_event(QuitEvent(message.data.client_id))
        if isinstance(message, InitializeGameRequest):
            self.push_custom_event(InitializeGameEvent(message.data.client_id, message.data.configuration))
        if isinstance(message, StartGameRequest):
            self.push_custom_event(StartGameEvent(message.data.client_id))
        if isinstance(message, AssignPlayerEntityRequest):
            self.push_custom_event(AssignPlayerEvent(message.data.client_id))
        if isinstance(message, MoveEntityRequest):
            self.push_custom_event(MoveEntityEvent(message.data.client_id, message.data.direction))
        if isinstance(message, AddBombRequest):
            self.push_custom_event(AddBombEvent(message.data.client_id))
        if isinstance(message, PrintMessageRequest):
            print("Host received message from client : %s" % message.data.message)

    def create_game(self, game_configuration):
        self.game = Game(self, game_configuration)

    def send_message(self, data):
        self.bus.send_message(data)

    def disconnect_from_client(self, client_id, client):
        self.bus.close_socket(client)
        if self.owner == client_id:
            self.shut_down()

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
                    if isinstance(event, SendMessage):
                        self.send_message(event.message)
                    if isinstance(event, InitializeGameEvent):
                        self.create_game(event.game_configuration)
                    if isinstance(event, AssignPlayerEvent):
                        self.game.assign_player_to_client(event.client_id)
                    if isinstance(event, MoveEntityEvent):
                        self.game.move_entity(event.client_id, event.direction)
                    if isinstance(event, AddBombEvent):
                        self.game.drop_bomb(event.client_id)
                    if isinstance(event, StartGameEvent):
                        self.game.start_game()
                    if isinstance(event, ClientDisconnectionEvent):
                        self.disconnect_from_client(event.client_id, event.socket_data)
                else:
                    self.logger.debug("Host disallowed event %s because client_id %s does not match %s" % (str(event), str(event.client_id), str(self.owner)))
            if self.game is not None:
                self.game.update_game()
        self.shut_down()
        self.logger.info("Host shut down")


def get_default_host_config():
    return host_configuration

