#!/usr/bin/python3
"""
Unit tests for the dogtail.tree Node Values.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402


import os
import unittest

try:
    from tests.test_gtk_demo import Gtk3DemoTest
except ImportError:
    from test_gtk_demo import Gtk3DemoTest


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk3-demo"), "Skipping, no gtk3-demo.")
class TestGtk3DogtailNodeValue(Gtk3DemoTest):
    """
    Class to test dogtail's Node Value.
    """

    def test_get_value(self):
        """
        Testing get value.
        """

        value_node = self.demo.child(role_name="scroll bar")
        self.assertEqual(value_node.value, 0)


    def test_set_value(self):
        """
        Testing set value.
        """

        self.demo.child("Source")
        value_node = self.demo.find_children(
            lambda x: x.role_name == "scroll bar"
        )[-1]
        value_node.value = 100

        self.assertEqual(value_node.value, 100)


    def test_get_min_value(self):
        """
        Testing get min value.
        """

        value_node = self.demo.child(role_name="scroll bar")
        self.assertEqual(value_node.min_value, 0)


    def test_set_min_value(self):
        """
        Testing set min value.
        """

        value_node = self.demo.child(role_name="scroll bar")
        with self.assertRaises(AttributeError):
            value_node.min_value = "not possible"


    def test_get_max_value(self):
        """
        Testing get max value.
        """

        self.demo.child("Source")
        value_node = self.demo.find_children(
            lambda x: x.role_name == "scroll bar"
        )[-1]

        self.assertTrue(value_node.max_value > 0)


    def test_set_max_value(self):
        """
        Testing set max value.
        """

        value_node = self.demo.child(role_name="scroll bar")
        with self.assertRaises(AttributeError):
            value_node.max_value = "not possible"


    def test_get_min_value_increment(self):
        """
        Testing get min value increment.
        """

        value_node = self.demo.child(role_name="scroll bar")
        self.assertNotEqual(value_node.min_value_increment, 0)


    def test_set_min_value_increment(self):
        """
        Testing set min value increment.
        """

        value_node = self.demo.child(role_name="scroll bar")
        with self.assertRaises(AttributeError):
            value_node.min_value_increment = "not possible"


if __name__ == "__main__":
    unittest.main()
