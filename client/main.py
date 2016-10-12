from .configuration import Configuration
from .messaging import MessageBus
from .view_states import MenuState
import uuid

class Client(object):
    def __init__(self):
        self.uuid = uuid.uuid4()
        self.configuration = Configuration()
        self.message_bus = MessageBus()
        self.state = MenuState()