import json


class BaseConfiguration(object):
    def __init__(self):
        pass

    @classmethod
    def option_classes(cls):
        """
        :return: a map of option classes - key is both the attribute name as well as the JSON key.
        """
        to_return = {}
        subclasses = ConfigurationOption.__subclasses__()
        while subclasses:
            subclass = subclasses.pop()
            if isinstance(subclass, ConfigurationOption):
                subclass_subclasses = subclass.__subclasses__()
                if not subclass_subclasses:
                    to_return[subclass.key()] = subclass
                else:
                    subclasses.extend(subclass_subclasses)
        return to_return

    def options(self):
        """
        :return: a map of currently set option classes
        """
        to_return = {}

        for attr in self.__dict__:
            value = getattr(self, attr)
            if isinstance(value, ConfigurationOption):
                to_return[attr] = value

        return to_return

    def load(self):
        """
        Load a series of key, value pairs from JSON into this object.

        If a key is unrecognized (and doesn't belong to any implemented Option classes), it becomes an
        UnidentifiedOption that ultimately will get removed from the configuration file.

        On FileNotFound or permission-related OSError exceptions, will do nothing.
        :return:
        """
        try:
            with open(self.filename, 'r') as f:
                option_classes = self.option_classes()
                option_dict = json.loads(f.read())
                for key in option_dict:
                    if key in option_classes:
                        option_class = option_classes[key]
                        option_value = option_dict[key]
                        try:
                            setattr(self, key, option_class(option_value))
                        except ConfigurationException:
                            pass
                    else:
                        setattr(self, key, UnidentifiedOption(key))
        except (OSError, FileNotFoundError):
            pass

    def save(self):
        """
        Write a series of key, value pairs of options in this object into a file.

        On any permissions related exceptions, won't do anything at all.
        :return:
        """
        opt_dict = {}
        options = self.options()
        for key in options:
            opt_dict[key] = options[key].value()
        try:
            with open(self.filename, 'w') as f:
                f.write(json.dumps(opt_dict))
        except OSError:
            pass


class DefaultConfiguration(BaseConfiguration):
    def __init__(self):
        super().__init__()


class Configuration(BaseConfiguration):
    def __init__(self, filename):
        """
        1.  Loads a default configuration.
        2.  Loads configuration from file.
        3.  Compares default configuration against loaded configuration.
        4.  Will remove entries that don't exist in the default configuration.
        5.  Will add entries that don't exist in the loaded configuration.
        6.  Will rewrite the configuration file if any modifications were required.
        """
        super().__init__()
        self.filename = filename

        # get the default configuration
        defaults = self.get_default_configuration()
        default_options = defaults.options()

        # load a configuration from a file
        self.load()
        curr_options = self.options()

        # add options in our default options that don't exist in the loaded options
        replace_options = []
        for key in default_options:
            if key not in curr_options or isinstance(curr_options[key], UnidentifiedOption):
                replace_options.append(default_options[key])

        # delete options in our loaded options that don't exist in our default options.
        delete_options = []
        for key in curr_options:
            if key not in default_options:
                delete_options.append(curr_options[key])

        for option in replace_options:
            setattr(self, option.key(), option)

        for option in delete_options:
            delattr(self, option.key())

        if len(delete_options) or len(replace_options):
            self.save()

    @classmethod
    def get_default_configuration(cls):
        """
        This will return a default configuration for this class.
        :return:
        """
        raise UnimplementedMethodException(cls, "get_default_configuration")


class ConfigurationOption(object):
    _key = None

    def __init__(self, value):
        self._value = None
        self.change(value)

    @classmethod
    def key(cls):
        return cls._key

    def validate(self, new_value):
        raise UnimplementedMethodException(self.__class__, "validate")

    def change(self, new_value):
        if self.validate(new_value):
            self._value = new_value
        else:
            raise ConfigurationException(self.__class__._key, new_value)

    def value(self):
        return self._value


class PredefinedConfigurationOption(ConfigurationOption):
    _options = None

    def __init__(self, value):
        super().__init__(value)

    @classmethod
    def options(cls):
        return cls._options

    def validate(self, new_value):
        return new_value in self.__class__.options()


class InputConfigurationOption(ConfigurationOption):
    def __init__(self, value):
        super().__init__(value)

    def validate(self, new_value):
        return new_value is not None


# This is only used when loading a configuration where a key doesn't match up to any other options.
# We overload the ConfigurationOption.key() method to make this work, and we don't care about the value it has.
class UnidentifiedOption(ConfigurationOption):
    def __init__(self, key):
        super().__init__(None)
        self._key = key

    def key(self):
        return self._key

    def validate(self, new_value):
        return True


class ConfigurationException(Exception):
    def __init__(self, key, value):
        super().__init__("The configuration for %s is invalid: %s" % (str(key), str(value)))


class UnimplementedMethodException(Exception):
    def __init__(self, cls, method):
        super().__init__("The method %s for class %s is unimplemented" % (str(method), str(cls)))
