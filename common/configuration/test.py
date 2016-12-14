from .configuration import *
import unittest
import os
import json


class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.configuration = TestConfiguration()

    def tearDown(self):
        if os.path.isfile(self.configuration.filename):
            os.remove(self.configuration.filename)

    def write_dict_to_file(self, dictionary):
        with open(self.configuration.filename, 'w') as f:
            f.write(json.dumps(dictionary))

    def read_dict_from_file(self):
        with open(self.configuration.filename, 'r') as f:
            stored_settings = json.loads(f.read())
        return stored_settings

    def test_new_configuration(self):
        """
        Test creating a new configuration
        :return:
        """
        self.assertIsNotNone(getattr(self.configuration, "username", None))
        self.assertIsNotNone(getattr(self.configuration, "screen_resolution", None))
        stored_settings = self.read_dict_from_file()
        self.assertTrue("screen_resolution" in stored_settings)
        self.assertTrue("username" in stored_settings)
        self.assertTrue(os.path.isfile(self.configuration.filename))

    def test_purge_unused_settings(self):
        """
        Test removing non-existent settings from a configuration file.
        :return:
        """
        self.write_dict_to_file({"test": "test"})
        self.configuration = TestConfiguration()
        stored_settings = self.read_dict_from_file()
        self.assertIsNone(getattr(self.configuration, "test", None))
        self.assertFalse("test" in stored_settings)
        self.assertTrue(os.path.isfile(self.configuration.filename))

    def test_add_new_settings(self):
        """
        Test adding new, non-existent settings to a configuration file
        :return:
        """
        self.write_dict_to_file({"username": "test"})
        self.configuration = TestConfiguration()
        stored_settings = self.read_dict_from_file()
        self.assertIsNotNone(self.configuration.screen_resolution)
        self.assertIsNotNone(self.configuration.username)
        self.assertTrue("username" in stored_settings)
        self.assertTrue("screen_resolution" in stored_settings)

    def test_bogus_configuration_settings(self):
        """
        Test overwriting configuration settings that will break things.
        :return:
        """
        self.write_dict_to_file({"screen_resolution": (1, 1)})
        self.configuration = TestConfiguration()
        stored_settings = self.read_dict_from_file()
        self.assertNotEquals(self.configuration.screen_resolution.value(), (1, 1))
        self.assertNotEquals(stored_settings["screen_resolution"], [1, 1])

    def test_valid_configuration_change(self):
        """
        Test programmatically changing a configuration value to a valid value.
        :return:
        """
        self.assertNotEquals(self.configuration.screen_resolution, (640, 480))
        self.configuration.screen_resolution.change((640, 480))
        self.assertEquals(self.configuration.screen_resolution.value(), (640, 480))

    def test_invalid_configuration_change(self):
        """
        Test programmatically changing a configuration to a default value, which should
        throw a ConfigurationException that we'll catch.
        :return:
        """
        self.assertNotEquals(self.configuration.screen_resolution, (1, 1))
        with self.assertRaises(ConfigurationException):
            self.configuration.screen_resolution.change((1, 1))
        self.assertNotEquals(self.configuration.screen_resolution.value(), (1, 1))


# We create a set of test configuration classes here.
class TestConfiguration(Configuration):
    def __init__(self, filename="test.ini"):
        self.username = None
        self.screen_resolution = None
        super().__init__(filename)

    @classmethod
    def get_default_configuration(cls):
        return DefaultTestConfiguration()


class DefaultTestConfiguration(BaseConfiguration):
    def __init__(self):
        super().__init__()
        self.username = UsernameOption("default")
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
