#!/usr/bin/python3
"""
Unit tests for the dogtail.tree Node.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402


import os
import unittest

from time import sleep

try:
    from tests.test_gtk_demo import Gtk4DemoTest
except ImportError:
    from test_gtk_demo import Gtk4DemoTest

from dogtail.tree import root, SearchError
from dogtail.config import config
from dogtail.rawinput import type_text, press_key

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk4-demo"), "Skipping, no gtk4-demo.")
class TestGtk4DogtailNode(Gtk4DemoTest):
    """
    Class to test dogtail's Node.
    """

    def test_not_existing_attribute(self):
        """
        Testing not existing attribute.
        """

        self.assertRaises(AttributeError, getattr, self.demo, "not_existing_attribute")


    def test_get_application_name(self):
        """
        Testing get application name.
        """

        self.assertEqual(self.demo.name, "gtk4-demo")


    def test_get_root_name(self):
        """
        Testing get root name.
        """

        self.assertEqual(root.name, "main")


    def test_set_name(self):
        """
        Testing setting a read only attribute.
        """

        self.assertRaises(AttributeError, self.demo.__setattr__, "name", "not possible")


    def test_get_application_role(self):
        """
        Testing get application role.
        """

        self.assertEqual(self.demo.role, Atspi.Role.APPLICATION)


    def test_set_application_role(self):
        """
        Testing set application role.
        """

        with self.assertRaises((RuntimeError, AttributeError)):
            self.demo.role = Atspi.Role.INVALID


    def test_get_application_role_name(self):
        """
        Testing get application role name.
        """

        self.assertEqual(self.demo.role_name, "application")


    def test_set_application_role_name(self):
        """
        Testing set application role name.
        """

        with self.assertRaises(AttributeError):
            self.demo.role_name = "not possible"


    def test_get_application_description(self):
        """
        Testing get application description.
        """

        self.assertEqual(self.demo.children[0].description, "")


    # TODO revisit this.
    @unittest.SkipTest
    def test_set_application_description(self):
        """
        Testing set application description.
        """

        # Does not appear to be the case. Interesting.
        with self.assertRaises(RuntimeError):
            self.demo.description = "not possible"


    def test_get_application_children(self):
        """
        Testing get application children.
        """

        self.assertIsNotNone(self.demo.children)
        self.assertTrue(isinstance(self.demo.children[0], Atspi.Accessible))


    def test_set_application_children(self):
        """
        Testing set application children.
        """

        with self.assertRaises(AttributeError):
            self.demo.children = []


    # TODO do we actually need children limit?
    @unittest.SkipTest
    def test_get_application_children_limit(self):
        """
        Testing get application children with limit.
        """

        config.children_limit = 1
        self.assertIsNotNone(self.demo.children)

        result = self.demo.child(role_name="tree table")
        self.assertEqual(len(result.children), 1)


    def test_get_application_parent(self):
        """
        Testing get application parent.
        """

        self.assertIsNotNone(self.demo.children)
        self.assertIsNotNone(self.demo.children[0].parent)
        self.assertEqual(self.demo.children[0].parent, self.demo)


    def test_set_application_parent(self):
        """
        Testing set application parent.
        """

        with self.assertRaises(AttributeError):
            self.demo.children[0].parent = None


    def test_get_application_text(self):
        """
        Testing get application text.
        """

        press_key("Esc")
        sleep(1)

        # Weird way to do this but it works as a unit test.
        window = None
        scroll_bar = self.demo.find_child(lambda x: x.role_name=="scroll bar" and x.showing)

        for _ in range(50):
            scroll_bar.value += 50
            sleep(1)
            try:
                clipboard_button = self.demo.child("Dialogs", retry=False)
                clipboard_button.double_click()
                sleep(1)

                window = self.demo.find_children(
                    lambda x: x.name == "Dialogs" and
                    x.role_name == "frame",
                    retry=False
                )[-1]

                break
            except (RuntimeError, SearchError):
                pass

        self.assertIsNotNone(window)

        entry_one = window.child(name="Entry 1", role_name="text")
        entry_two = window.child(name="", role_name="text")

        self.assertEqual(entry_one.text, "")
        self.assertEqual(entry_two.text, "")


    def test_set_application_text(self):
        """
        Testing set application text.
        """

        press_key("Esc")
        sleep(1)

        # Weird way to do this but it works as a unit test.
        scroll_bar = self.demo.child(role_name="scroll bar")
        for _ in range(50):
            scroll_bar.value += 50
            try:
                clipboard_button = self.demo.child("Dialogs", retry=False)
                clipboard_button.double_click()
                break
            except (RuntimeError, SearchError):
                pass

        window = self.demo.find_children(
            lambda x: x.name == "Dialogs" and
            x.role_name == "frame",
            retry=False
        )[-1]

        entry_one = window.child(name="Entry 1", role_name="text")
        entry_two = window.child(name="", role_name="text")

        # No longer works in gtk4.
        # entry_one.text = "test one"
        # entry_two.text = "test two"

        # Coordinates are wrong, offset it.
        entry_one.click()
        type_text("test one")


        # Coordinates are wrong, offset it.
        entry_two.click()
        type_text("test two")


        self.assertEqual(entry_one.text, "test one")
        self.assertEqual(entry_two.text, "test two")

    # Atspi does not throw error on this, no point to have failing test then.
    @unittest.SkipTest
    def test_set_application_text_on_non_text_interface(self):
        """
        Testing set application text.
        """

        with self.assertRaises(AttributeError):
            self.demo.text = "not possible"


    @unittest.SkipTest
    def test_get_relations(self):
        """
        Testing relations.
        """

        # We use this only for labels, lets keep the note if some other uses appear.


    # This is bugged in gtk4-demo, lets skip this test.
    @unittest.SkipTest
    def test_get_labelee(self):
        """
        Testing get labelee.
        """

        press_key("Esc")
        sleep(1)

        # Weird way to do this but it works as a unit test.
        scroll_bar = self.demo.child(role_name="scroll bar")
        for _ in range(50):
            scroll_bar.value += 50
            try:
                clipboard_button = self.demo.child("Dialogs", retry=False)
                clipboard_button.double_click()
                break
            except (RuntimeError, SearchError):
                pass

        window = self.demo.find_children(
            lambda x: x.name == "Dialogs" and
            x.role_name == "frame",
            retry=False
        )[-1]

        entry_one = window.child(name="Entry 1", role_name="label")
        self.assertEqual(entry_one.labelee.role_name, "text")


    def test_set_labelee(self):
        """
        Testing set labelee.
        """

        with self.assertRaises(AttributeError):
            self.demo.labelee = None


    def test_get_labeler(self):
        """
        Testing get labeler.
        """

        press_key("Esc")
        sleep(1)

        # Weird way to do this but it works as a unit test.
        scroll_bar = self.demo.child(role_name="scroll bar")
        for _ in range(50):
            scroll_bar.value += 50
            try:
                clipboard_button = self.demo.child("Dialogs", retry=False)
                clipboard_button.double_click()
                sleep(1)

                window = self.demo.find_children(
                    lambda x: x.name == "Dialogs" and
                    x.role_name == "frame",
                    retry=False
                )[-1]

                break
            except (RuntimeError, SearchError):
                pass


        entry_one_labelee = window.child(name="Entry 1", role_name="text")
        self.assertEqual(entry_one_labelee.labeler.role_name, "label")


    def test_set_labeler(self):
        """
        Testing set labeler.
        """

        with self.assertRaises(AttributeError):
            self.demo.labeler = None


    def test_get_actions(self):
        """
        Testing get actions.
        """

        self.assertEqual(len(self.demo.actions), 0)


    def test_set_actions(self):
        """
        Testing set actions.
        """

        with self.assertRaises(AttributeError):
            self.demo.actions = {}


    def test_get_extents(self):
        """
        Testing get extents.
        """

        (x_position, y_position, width, height) = self.demo.children[0].extents

        self.assertTrue(x_position >= 0)
        self.assertTrue(y_position >= 0)
        self.assertTrue(width > 0)
        self.assertTrue(height > 0)


    def test_get_from_wrong_node(self):
        """
        Testing get extents but some nodes do not provide it.
        """

        self.assertIsNone(self.demo.extents)


    def test_set_extents(self):
        """
        Testing set extents.
        """

        with self.assertRaises(AttributeError):
            self.demo.extents = (0, 0, 500, 500)


    def test_get_position(self):
        """
        Testing get position.
        """

        (x_position, y_position) = self.demo.children[0].position
        self.assertTrue(isinstance(x_position, int))
        self.assertTrue(isinstance(y_position, int))


    def test_get_position_from_wrong_node(self):
        """
        Testing get position but some nodes do not provide it.
        """

        # The root object does not have Component Interface - we return (-1, -1)
        self.assertEqual(self.demo.position, (-1, -1))


    def test_set_position(self):
        """
        Testing set position.
        """

        with self.assertRaises(AttributeError):
            self.demo.position = (500, 500)


    def test_get_size(self):
        """
        Testing get size.
        """

        (x_size, y_size) = self.demo.children[0].size
        self.assertTrue(isinstance(x_size, int))
        self.assertTrue(isinstance(y_size, int))
        self.assertTrue(x_size > 0)
        self.assertTrue(y_size > 0)


    def test_get_size_from_wrong_node(self):
        """
        Testing get size but some nodes do not provide it.
        """

        # The root object does not have Component Interface - we return (-1, -1)
        self.assertEqual(self.demo.size, (-1, -1))


    def test_set_size(self):
        """
        Testing set size.
        """

        with self.assertRaises(AttributeError):
            self.demo.size = (500, 500)


    def test_get_toolkit(self):
        """
        Testing get toolkit.
        """

        self.assertIsNotNone(self.demo.toolkit)


    def test_set_toolkit(self):
        """
        Testing set toolkit.
        """

        with self.assertRaises(AttributeError):
            self.demo.toolkit = "not possible"


    def test_get_id(self):
        """
        Testing get Id.
        """

        self.assertIsNotNone(self.demo.id)


    def test_set_id(self):
        """
        Testing set id.
        """

        with self.assertRaises(AttributeError):
            self.demo.id = "not possible"


if __name__ == "__main__":
    unittest.main()
