import json, os

class ConfigurationData:
    class Keys:
        SCREEN_SIZE="screen_size"

    def __init__(self, key, value, text, options=None):
        self.key = key
        self.value = value
        self.text = text
        self.options = options

    @staticmethod
    def default_configuration():
        return {
            ConfigurationData.Keys.SCREEN_SIZE:ConfigurationData(ConfigurationData.Keys.SCREEN_SIZE, (800, 600), "Screen Size", [(640, 480), (800, 600), (1024, 768)])
        }

class Configuration(object):
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.configuration = ConfigurationData.default_configuration()

        # if we have a config file, we replace our default configuration
        # with whatever values are in the file
        if os.path.isfile(Configuration.CONFIG_FILE):
            self.read_configuration_from_file()

        # finally, we write our configuration back out - this cleans up the file
        # from having old options that no longer exist.
        self.write_configuration_to_file()

    def write_configuration_to_file(self):
        config_file = open(Configuration.CONFIG_FILE, "w")
        to_write = {}
        for key in self.configuration:
            to_write[key] = self.configuration[key].value
        config_file.write(json.dumps(to_write))
        config_file.close()

    def read_configuration_from_file(self):
        config_file = open(Configuration.CONFIG_FILE, "r")
        data = config_file.read()
        config_file.close()
        loaded_data = json.loads(data)
        for key in loaded_data:
            if key in self.configuration:
                value = loaded_data[key]
                self.configuration[key].value = value

    def get_screen_size(self):
        return self.configuration[ConfigurationData.Keys.SCREEN_SIZE]
