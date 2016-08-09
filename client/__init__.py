from . import sdl2_path
import uuid, sys, sdl2, sdl2.ext, threading
from common import get_logger
from common.messaging.messages import *
from common.messaging import MessageBus
from host import Host
from .view_states import *
from .custom_events import *


class Client(object):
    def __init__(self, configuration):
        self.id = uuid.uuid4()
        self.logger = get_logger(self)
        self.shutting_down = False
        self.configuration = configuration
        self.custom_events = []
        self.state = None
        self.bus = None
        self.host = None
        self.host_thread = None

    def create_host(self, host_configuration):
        self.logger.debug("Creating Host")
        self.host = Host(self.id, host_configuration)
        self.host_thread = threading.Thread(name="Host-Thread", target=self.host.run)
        self.host_thread.start()

    def connect_to_host(self, host_configuration):
        if self.bus is None:
            self.bus = MessageBus(self.configuration.socket_data, self.receive_message)
            self.bus.connect(host_configuration.socket_data)
            self.send_message(ConnectionRequest(self.configuration.socket_data))

    def receive_message(self, message):
        self.logger.info("Received message : %s" % str(message))

    def send_message(self, message):
        message.data.client_id = self.id
        self.bus.send_message(message)

    def disconnect_from_host(self):
        if self.bus is not None:
            self.send_message(DisconnectionRequest(self.configuration.socket_data))
            self.send_message(HostShutdownMessage())
            self.bus.shut_down()
            self.bus = None

    def shut_down(self):
        if self.state is not None:
            self.state.clean_up()
            self.state = None
        self.disconnect_from_host()

    def push_custom_event(self, event):
        self.custom_events.append(event)

    def get_custom_events(self):
        to_return = self.custom_events
        self.custom_events = []
        return to_return

    def log_event(self, event):
        self.logger.debug("Received event %s" % str(event))

    def change_view_state(self, next_state_class):
        self.logger.info("Changing state to %s" % str(next_state_class.__name__))
        self.state.clean_up()
        self.state = next_state_class(self)

    def run(self):
        self.logger.info("Client started")
        sdl2.ext.init()
        window = sdl2.ext.Window(self.configuration.game_name, size=self.configuration.screen_size)
        window.show()
        self.state = MenuState(self)
        while not self.shutting_down:
            events = sdl2.ext.get_events()
            other_events = self.get_custom_events()
            events.extend(other_events)
            for event in events:
                if isinstance(event, CustomEvent):
                    self.log_event(event)
                    if isinstance(event, SendMessage):
                        self.send_message(event.message)
                    elif isinstance(event, CreateHost):
                        self.create_host(event.configuration)
                    elif isinstance(event, ConnectToHost):
                        self.connect_to_host(event.configuration)
                    elif isinstance(event, DisconnectFromHost):
                        self.disconnect_from_host()
                    elif isinstance(event, QuitEvent):
                        self.shutting_down = True
                        break
                    elif isinstance(event, ViewStateChange):
                        self.change_view_state(event.next_state)
                elif event.type == sdl2.SDL_QUIT:
                    self.shutting_down = True
                    break
                self.state.process_event(event)
            window.refresh()
        self.shut_down()
        return 0

