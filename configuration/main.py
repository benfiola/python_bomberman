import json, os


class ConfigurationKeys(object):
    SCREEN_SIZE = "screen_size"


class Configuration(object):
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.configuration = {}
        default_configuration = self.default_configuration()

        # if we don't have a config file, make it and store the default configuration
        if not os.path.isfile(Configuration.CONFIG_FILE):
            self.configuration = default_configuration
            self.write_configuration_to_file()
        else:
            # if we do have a config file, try to read from it.
            # if it fails, rewrite the config file with default values
            try:
                self.read_configuration_from_file()
            except ValueError:
                self.configuration = default_configuration
                self.write_configuration_to_file()

        # add any new configuration entries from our default ocnfiguration into
        # the configuration we've read from the file.
        should_rewrite_file = False
        for key in default_configuration:
            if key not in self.configuration:
                should_rewrite_file = True
                self.configuration[key] = default_configuration[key]

        # if our read configuration contains entries that don't exist in our
        # default configuration, then we erase them from dictionary and rewrite
        # the file.
        keys_to_remove = []
        for key in self.configuration:
            if key not in default_configuration:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            should_rewrite_file = True
            self.configuration.pop(key, None)

        if should_rewrite_file:
            self.write_configuration_to_file()

    def default_configuration(self):
        return {
            ConfigurationKeys.SCREEN_SIZE: (800, 600)
        }

    def write_configuration_to_file(self):
        config_file = open(Configuration.CONFIG_FILE, "w")
        config_file.write(json.dumps(self.configuration))
        config_file.close()

    def read_configuration_from_file(self):
        config_file = open(Configuration.CONFIG_FILE, "r")
        data = config_file.read()
        config_file.close()
        self.configuration = json.loads(data)

    def get_screen_size(self):
        return self.configuration[ConfigurationKeys.SCREEN_SIZE]
