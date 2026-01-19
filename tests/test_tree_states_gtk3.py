#!/usr/bin/python3
"""
Unit tests for the dogtail.tree Node States.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402


import os
import unittest
from time import sleep

try:
    from tests.test_gtk_demo import Gtk3DemoTest
except ImportError:
    from test_gtk_demo import Gtk3DemoTest

from dogtail.tree import root, Node


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk3-demo"), "Skipping, no gtk3-demo.")
class TestGtk3DogtailNodeStates(Gtk3DemoTest):
    """
    Class to test dogtail's Node States.
    """


    def test_get_selected(self):
        """
        Testing get selected.
        """

        info_node = self.demo.child("Info")
        self.assertTrue(info_node.selected)


    def test_set_selected(self):
        """
        Testing get selected.
        """

        info_node = self.demo.child("Info")
        with self.assertRaises(AttributeError):
            info_node.selected = "not possible"


    def test_get_selectable(self):
        """
        Testing get selectable.
        """

        info_node = self.demo.child("Info")
        self.assertTrue(info_node.selected)


    def test_set_selectable(self):
        """
        Testing get selectable.
        """


        info_node = self.demo.child("Info")
        with self.assertRaises(AttributeError):
            info_node.selectable = "not possible"


    def test_get_sensitive(self):
        """
        Testing get sensitive.
        """

        self.assertFalse(self.demo.sensitive)
        self.assertTrue(self.demo.children[0].sensitive)


    def test_set_sensitive(self):
        """
        Testing set sensitive.
        """

        with self.assertRaises(AttributeError):
            self.demo.sensitive = True


    def test_get_showing(self):
        """
        Testing get showing.
        """

        self.assertFalse(self.demo.showing)
        self.assertTrue(self.demo.children[0].showing)


    def test_set_showing(self):
        """
        Testing set showing.
        """

        with self.assertRaises(AttributeError):
            self.demo.showing = True


    def test_get_visible(self):
        """
        Testing get visible.
        """

        self.assertFalse(self.demo.visible)
        self.assertTrue(self.demo.children[0].visible)


    def test_set_visible(self):
        """
        Testing set visible.
        """

        with self.assertRaises(AttributeError):
            self.demo.visible = True


    def test_checked(self):
        """
        Testing checked.
        """

        self.run_demo("Application Class")
        application = root.application("gtk3-demo-application")

        # Sometimes on wrong coordinates, we can use actions or select.
        application.child("Preferences", "menu").select()
        sleep(1)

        menu_item = application.child("Prefer Dark Theme")
        self.assertFalse(menu_item.checked)

        application.child("Prefer Dark Theme").do_action_named("click")
        sleep(1)

        menu_item = application.child("Prefer Dark Theme")
        self.assertTrue(menu_item.checked)


    def test_dead_empty(self):
        """
        Testing is dead method by empty Node.
        """

        node = Node()
        self.assertTrue(node.dead)


    def test_dead_by_dead_application(self):
        """
        Testing is dead method by dead Application.
        """

        self.assertFalse(self.demo.dead)
        # Close the application.
        self.process.kill()
        self.process.wait()
        sleep(5)

        self.assertTrue(self.demo.dead)


if __name__ == "__main__":
    unittest.main()
