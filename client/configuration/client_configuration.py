from common import BaseConfiguration, Configuration, InputConfigurationOption, PredefinedConfigurationOption, ConfigurationException


class ClientConfiguration(Configuration):
    def __init__(self, filename="client_config.ini"):
        self.username = None
        self.screen_resolution = None
        super().__init__(filename)

    @classmethod
    def get_default_configuration(cls):
        return DefaultClientConfiguration()


class DefaultClientConfiguration(BaseConfiguration):
    def __init__(self):
        super().__init__()
        self.username = UsernameOption("Default")
        self.screen_resolution = ScreenResolutionOption((800, 600))


class UsernameOption(InputConfigurationOption):
    _key = "username"

    def __init__(self, value):
        super().__init__(str(value))


class ScreenResolutionOption(PredefinedConfigurationOption):
    _key = "screen_resolution"
    _options = [(640, 480), (800, 600), (1024, 768)]

    def __init__(self, value):
        super().__init__(tuple(value))
