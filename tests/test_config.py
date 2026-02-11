#!/usr/bin/python3
"""
Unit tests for the dogtail.config.
"""

import unittest
from dogtail.config import config


class TestConfig(unittest.TestCase):
    """
    Class to test dogtail's config.
    """

    def test_set_value(self):
        """
        Testing set value.
        """

        self.assertEqual(config.action_delay, 1.0)
        config.action_delay = 2.0
        self.assertEqual(config.action_delay, 2.0)


    def test_set_incorrect_value(self):
        """
        Testing set incorrect value.
        """

        with self.assertLogs("__dogtail_logger__", level="INFO") as captured_message:
            config.action_delay = "set_string_to_int_or_float_accepted_value"

            expected_messages = [
                "Attempt to set value of type '<class 'str'>' to key with accepted types '[<class 'float'>, <class 'int'>]'",
                "Fallback of config option 'action_delay' to '1'.",
            ]

            for record in captured_message.records:
                self.assertEqual(record.levelname, "INFO")
                self.assertIn(record.msg, expected_messages)


    def test_set_not_existing_value(self):
        """
        Testing set not existing value.
        """

        with self.assertRaises(AttributeError):
            config.not_existing = False


    def test_get_value(self):
        """
        Testing get value.
        """

        self.assertEqual(config.action_delay, 1.0)


    def test_get_incorrect_value(self):
        """
        Testing get not existing value.
        """

        self.assertRaises(AttributeError, getattr, config, "not_existing")


    def test_reset_configuration(self):
        """
        Testing resetting the configuration.
        """

        # When running unit tests we manipulate the config, reset it first.
        config.reset_configuration()


        original_action_delay = config.action_delay
        self.assertEqual(config.action_delay, original_action_delay)
        original_default_delay = config.default_delay
        self.assertEqual(config.default_delay, original_default_delay)

        config.action_delay = 2.0
        config.default_delay = 2.0

        self.assertNotEqual(config.action_delay, original_action_delay)
        self.assertNotEqual(config.default_delay, original_default_delay)

        config.reset_configuration()

        self.assertEqual(config.action_delay, original_action_delay)
        self.assertEqual(config.default_delay, original_default_delay)


if __name__ == "__main__":
    unittest.main()
