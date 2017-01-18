import threading
from common import *
from .platform_utils import Platform
Platform.get_platform().configure_paths()
import logging
import client.configuration as configuration
import client.events as events
import client.controllers.intro as controller
import common.messaging.message_bus as message_bus
import sdl2.ext
import time
import uuid as uuid_lib
import host.host as host


class Client(object):
    def __init__(self):
        self.logger = logging.getLogger("client")
        self.uuid = "client"
        self.event_list = []
        self.event_handlers = {}
        self.event_list_lock = threading.Lock()
        self.shutting_down = False
        self.message_bus = None
        self.local_message_bus = message_bus.LocalMessageBus(self.uuid)
        self.remote_message_bus = message_bus.ClientNetworkedMessageBus(self.uuid)
        self.controller = None
        self.host = None
        self.platform = Platform.get_platform()
        self.configuration = configuration.ClientConfiguration()
        self.fps_counter = FPSCounter()

        self.register_event_handler(events.Quit, self.begin_shut_down)
        self.register_event_handler(events.ControllerTransition, self.controller_transition)
        self.register_event_handler(events.CreateHost, self.create_host)
        self.register_event_handler(events.StartMessageBus, self.start_message_bus)
        self.register_event_handler(events.StopMessageBus, self.stop_message_bus)
        self.register_event_handler(events.SendRequest, self.send_message)

        self.window = sdl2.ext.Window("Bomberman", size=self.configuration.screen_resolution.value())

        self.add_event(events.ControllerTransition(controller.IntroController))
        self.window.show()

    def create_host(self, event):
        host_data = event.host_data
        if host_data.local:
            self.host = host.LocalHost(self.local_message_bus)
        else:
            self.host = host.MultiplayerHost(self.uuid, host_data.address[1])

    def start_message_bus(self, event):
        host_data = event.host_data
        if host_data.local:
            self.message_bus = self.local_message_bus
        else:
            self.message_bus = self.remote_message_bus
        self.message_bus.start(host_data.address)

    def stop_message_bus(self, event=None):
        if self.host:
            self.host.stop()
        self.message_bus.stop()
        self.remove_event_handlers(self.message_bus)

    def send_message(self, event):
        self.message_bus.send(event.request)

    def begin_shut_down(self, _):
        self.shutting_down = True

    def shut_down(self):
        if self.message_bus is not None:
            self.stop_message_bus()
        self.controller._tear_down()
        self.remove_event_handlers(self)

    def controller_transition(self, event):
        if self.controller:
            self.controller._tear_down()
        self.controller = event.controller_class(self)
        self.controller._set_up()

    def handle_event(self, event):
        evt_cls = event.__class__
        if evt_cls in self.event_handlers:
            for handler in self.event_handlers[evt_cls]:
                handler(event)

    def register_event_handler(self, evt_cls, callback):
        if evt_cls not in self.event_handlers:
            self.event_handlers[evt_cls] = []
        self.event_handlers[evt_cls].append(callback)

    def remove_event_handlers(self, owner):
        for key in self.event_handlers.keys():
            for handler in list(self.event_handlers[key]):
                if handler.__self__ and handler.__self__ == owner:
                    self.event_handlers[key].remove(handler)

    def add_event(self, event):
        with self.event_list_lock:
            self.event_list.append(event)

    def get_events(self):
        sdl_events = sdl2.ext.get_events()
        events = []
        for sdl_event in sdl_events:
            events.append(self.convert_sdl2_event(sdl_event))
        with self.event_list_lock:
            events.extend(self.event_list)
            self.event_list = []
        return events

    @staticmethod
    def convert_sdl2_event(event):
        if isinstance(event, sdl2.events.SDL_Event):
            if event.type == sdl2.SDL_QUIT:
                return events.Quit()
            if event.type == sdl2.SDL_KEYDOWN:
                return events.KeyInputDown(events.KeyInputDown.convert_from_sdl2(event.key.keysym.sym))
            if event.type == sdl2.SDL_KEYUP:
                return events.KeyInputUp(events.KeyInputUp.convert_from_sdl2(event.key.keysym.sym))
        return event

    def run(self):
        self.fps_counter.start()
        while not self.shutting_down:
            events = self.get_events()
            for event in events:
                self.handle_event(event)
            self.controller.process()
            self.fps_counter.process_frame()
        self.shut_down()


class FPSCounter(object):
    def __init__(self):
        self.logger = logging.getLogger("fps-counter")
        self.time = time.time()
        self.frames = 0

    def start(self):
        self.reset()

    def reset(self):
        self.time = time.time()
        self.frames = 0

    def process_frame(self):
        curr_time = time.time()
        if curr_time - self.time >= 1:
            self.logger.debug("%d frames per second." % self.frames)
            self.reset()
        else:
            self.frames += 1






