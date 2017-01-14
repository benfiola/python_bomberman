import logging
import common.messaging.message_bus as message_bus
import common.messaging.messages as messages
import uuid as uuid_lib
import threading
import time

class Host(object):
    def __init__(self, bus, owner, uuid):
        self.logger = logging.getLogger("host")
        self.shutting_down = False
        self.owner = owner
        self.uuid = uuid
        self.message_bus = bus
        self.events_lock = threading.Lock()
        self.events = []
        self.connected_clients = set()

        self.message_bus.register_data_handler(messages.CreateGame, self.create_game)
        self.message_bus.register_data_handler(messages.Print, self.print)
        self.main_thread = threading.Thread(name="host", target=self.run)
        self.main_thread.start()

    def get_events(self):
        with self.events_lock:
            to_return = list(self.events)
        return to_return

    def add_event(self, event):
        with self.events_lock:
            self.events.append(event)

    def print(self, request):
        self.logger.info("print received: %s" % request.message)

    def create_game(self, request):
        self.logger.info("create game request received")

    def stop(self):
        self.shutting_down = True
        self.message_bus.stop()
        self.main_thread.join()

    def process_event(self, event):
        pass

    def run(self):
        while not self.shutting_down:
            events = self.get_events()
            for event in events:
                self.process_event(event)
            time.sleep(.1)
        self.logger.info("host shut down")


class LocalHost(Host):
    def __init__(self, bus):
        super().__init__(bus, bus.uuid, uuid_lib.uuid4())


class MultiplayerHost(Host):
    def __init__(self, owner, host_port, uuid="host"):
        super().__init__(message_bus.HostNetworkedMessageBus(uuid, host_port), owner, uuid)
        self.message_bus.start()

