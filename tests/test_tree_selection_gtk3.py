#!/usr/bin/python3
"""
Unit tests for the dogtail.tree Node Selection.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402


import os
import unittest

from time import sleep

from dogtail.tree import SearchError
from dogtail.rawinput import press_key

try:
    from tests.test_gtk_demo import Gtk3DemoTest
except ImportError:
    from test_gtk_demo import Gtk3DemoTest


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk3-demo"), "Skipping, no gtk3-demo.")
class TestGtk3DogtailNodeSelection(Gtk3DemoTest):
    """
    Class to test dogtail's Node Selection.
    """

    def test_select_simple(self):
        """
        Testing select simple.
        """

        info_node = self.demo.child("Info")
        source_node = self.demo.child("Source")

        self.assertTrue(info_node.selected)
        self.assertFalse(source_node.selected)

        source_node.select()

        self.assertFalse(info_node.selected)
        self.assertTrue(source_node.selected)


    def test_select(self):
        """
        Testing select.
        """

        # Weird way to do this but it works as a unit test.
        self.demo.child("Icon View").click()
        press_key("+")
        self.run_demo("Icon View Basics")

        window = self.demo.find_children(
            lambda x: x.name == "Icon View Basics" and
            x.role_name == "frame"
        )[-1]

        layered_pane = window.child(role_name="layered pane")

        self.assertFalse(layered_pane.children[1].selected)
        layered_pane.children[1].select()
        self.assertTrue(layered_pane.children[1].selected)


    def test_deselect(self):
        """
        Testing deselect.
        """

        press_key("Esc")
        sleep(1)

        # Weird way to do this but it works as a unit test.
        scroll_bar = self.demo.find_child(lambda x: x.role_name == "scroll bar" and x.showing)
        for _ in range(20):
            scroll_bar.value += 100

            self.demo.child("Icon View").click()
            sleep(0.5)
            press_key("+")

            try:
                self.run_demo("Icon View Basics")
                break
            except (RuntimeError, SearchError):
                sleep(1)

        window = self.demo.find_children(
            lambda x: x.name == "Icon View Basics" and
            x.role_name == "frame"
        )[-1]

        layered_pane = window.child(role_name="layered pane")

        layered_pane.children[1].select()
        self.assertTrue(layered_pane.children[1].selected)

        layered_pane.children[1].deselect()
        self.assertFalse(layered_pane.children[1].selected)


    def test_select_all(self):
        """
        Testing select all.
        """

        # Weird way to do this but it works as a unit test.
        self.demo.child("Icon View").click()
        press_key("+")
        self.run_demo("Icon View Basics")

        window = self.demo.find_children(
            lambda x: x.name == "Icon View Basics" and
            x.role_name == "frame"
        )[-1]

        layered_pane = window.child(role_name="layered pane")

        self.assertFalse(layered_pane.children[0].selected)
        self.assertFalse(layered_pane.children[1].selected)
        self.assertFalse(layered_pane.children[2].selected)

        layered_pane.select_all()

        self.assertTrue(layered_pane.children[0].selected)
        self.assertTrue(layered_pane.children[1].selected)
        self.assertTrue(layered_pane.children[2].selected)


    def test_deselect_all(self):
        """
        Testing deselect all.
        """

        # Weird way to do this but it works as a unit test.
        self.demo.child("Icon View").click()
        press_key("+")
        self.run_demo("Icon View Basics")

        window = self.demo.find_children(
            lambda x: x.name == "Icon View Basics" and
            x.role_name == "frame"
        )[-1]

        layered_pane = window.child(role_name="layered pane")

        layered_pane.select_all()

        self.assertTrue(layered_pane.children[0].selected)
        self.assertTrue(layered_pane.children[1].selected)
        self.assertTrue(layered_pane.children[2].selected)

        layered_pane.deselect_all()

        self.assertFalse(layered_pane.children[0].selected)
        self.assertFalse(layered_pane.children[1].selected)
        self.assertFalse(layered_pane.children[2].selected)


if __name__ == "__main__":
    unittest.main()
