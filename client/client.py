import threading

from common import *
import client.configuration as configuration
from .platform_utils import Platform
import client.events as events
import client.controllers as controllers

platform = Platform.get_platform()
import sdl2.ext


class Client(object):
    def __init__(self):
        self.logger = logging.getLogger("client")
        self.event_list = []
        self.event_handlers = {}
        self.event_list_lock = threading.Lock()
        self.shutting_down = False
        self.message_bus = None
        self.platform = platform
        self.configuration = configuration.ClientConfiguration()

        self.register_event_handler(events.Quit, self.begin_shut_down)
        self.register_event_handler(events.ControllerTransition, self.controller_transition)

        self.window = sdl2.ext.Window("Bomberman", size=self.configuration.screen_resolution.value())

        self.controller = controllers.IntroController(self)
        self.controller.set_up()

        self.window.show()

    def start_message_bus(self, host_data):
        self.message_bus.start(host_data)

    def stop_message_bus(self):
        self.message_bus.stop()
        self.remove_event_handlers(self.message_bus)

    def begin_shut_down(self, _):
        self.shutting_down = True

    def shut_down(self):
        if self.message_bus is not None:
            self.stop_message_bus()
        self.controller.tear_down()
        self.remove_event_handlers(self)

    def controller_transition(self, event):
        self.controller.tear_down()
        self.controller = event.controller_class(self)
        self.controller.set_up()

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
        while not self.shutting_down:
            events = self.get_events()
            for event in events:
                self.handle_event(event)
            self.controller.process()
        self.shut_down()





