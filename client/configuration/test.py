from .configuration import *
import unittest
import os
import json


class ConfigurationTest(unittest.TestCase):
    FILENAME="test.ini"

    def tearDown(self):
        if os.path.isfile(self.FILENAME):
            os.remove(self.FILENAME)

    def write_dict_to_file(self, dictionary):
        with open(self.FILENAME, 'w') as f:
            f.write(json.dumps(dictionary))

    def read_dict_from_file(self):
        with open(self.FILENAME, 'r') as f:
            stored_settings = json.loads(f.read())
        return stored_settings

    def test_new_configuration(self):
        """
        Test creating a new configuration
        :return:
        """
        configuration = Configuration(filename=self.FILENAME)
        self.assertIsNotNone(getattr(configuration, "username", None))
        self.assertIsNotNone(getattr(configuration, "screen_resolution", None))
        stored_settings = self.read_dict_from_file()
        self.assertTrue("screen_resolution" in stored_settings)
        self.assertTrue("username" in stored_settings)
        self.assertTrue(os.path.isfile(self.FILENAME))

    def test_purge_unused_settings(self):
        """
        Test removing non-existent settings from a configuration file.
        :return:
        """
        self.write_dict_to_file({"test": "test"})
        configuration = Configuration(filename=self.FILENAME)
        stored_settings = self.read_dict_from_file()
        self.assertIsNone(getattr(configuration, "test", None))
        self.assertFalse("test" in stored_settings)
        self.assertTrue(os.path.isfile(self.FILENAME))

    def test_add_new_settings(self):
        """
        Test adding new, non-existent settings to a configuration file
        :return:
        """
        self.write_dict_to_file({"username": "test"})
        configuration = Configuration(filename=self.FILENAME)
        stored_settings = self.read_dict_from_file()
        self.assertIsNotNone(configuration.screen_resolution)
        self.assertIsNotNone(configuration.username)
        self.assertTrue("username" in stored_settings)
        self.assertTrue("screen_resolution" in stored_settings)

    def test_bogus_configuration_settings(self):
        """
        Test overwriting configuration settings that will break things.
        :return:
        """
        self.write_dict_to_file({"screen_resolution": (1, 1)})
        configuration = Configuration(filename=self.FILENAME)
        stored_settings = self.read_dict_from_file()
        self.assertNotEquals(configuration.screen_resolution.value(), (1, 1))
        self.assertNotEquals(stored_settings["screen_resolution"], [1, 1])

    def test_valid_configuration_change(self):
        """
        Test programmatically changing a configuration value to a valid value.
        :return:
        """
        configuration = Configuration(filename=self.FILENAME)
        self.assertNotEquals(configuration.screen_resolution, (640, 480))
        configuration.screen_resolution.change((640, 480))
        self.assertEquals(configuration.screen_resolution.value(), (640, 480))

    def test_invalid_configuration_change(self):
        """
        Test programmatically changing a configuration to a default value, which should
        throw a ConfigurationException that we'll catch.
        :return:
        """
        configuration = Configuration(filename=self.FILENAME)
        self.assertNotEquals(configuration.screen_resolution, (1, 1))
        with self.assertRaises(ConfigurationException):
            configuration.screen_resolution.change((1, 1))
        self.assertNotEquals(configuration.screen_resolution.value(), (1, 1))
