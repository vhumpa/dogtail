#!/usr/bin/python3
"""
Unit tests for the dogtail.utils accessibility.
"""


import unittest

from dogtail.utils import (
    enable_accessibility,
    is_accessibility_enabled,
    bail_because_accessibility_is_disabled
)


class TestAccessibility(unittest.TestCase):
    """
    Class to test dogtail's utils accessibility methods.
    """

    def test_a11y_enable(self):
        """
        Test utils accessibility with enable.
        """

        enable_accessibility()
        self.assertTrue(is_accessibility_enabled())


    def test_bail_when_a11y_disabled(self):
        """
        Test utils accessibility with bail on disabled state.
        """

        with self.assertRaises(SystemExit):
            bail_because_accessibility_is_disabled()


if __name__ == "__main__":
    unittest.main()
