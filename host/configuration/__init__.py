import common.configuration as configuration


class HostConfiguration(configuration.Configuration):
    def __init__(self, filename="host_config.ini"):
        self.address = None
        self.port = None
        super().__init__(filename)

    @classmethod
    def get_default_configuration(cls):
        return DefaultHostConfiguration()


class DefaultHostConfiguration(configuration.BaseConfiguration):
    def __init__(self):
        super().__init__()
        self.address = HostAddressOption("127.0.0.1")
        self.port = HostPortOption(40000)


class HostAddressOption(configuration.InputConfigurationOption):
    _key = "address"

    def __init__(self, value):
        super().__init__(str(value))


class HostPortOption(configuration.InputConfigurationOption):
    _key = "port"

    def __init__(self, value):
        super().__init__(int(value))
