from common import *
from .configuration import ClientConfiguration
from .platform_utils import Platform

class Client(object):
    def __init__(self):
        self.message_bus = None
        self.configuration = ClientConfiguration()
        self.logger = logging.getLogger("client")
        self.platform = Platform.get_platform()

        import sdl2.ext
        self.window = sdl2.ext.Window("Bomberman", size=self.configuration.screen_resolution.value())
        self.window.show()


