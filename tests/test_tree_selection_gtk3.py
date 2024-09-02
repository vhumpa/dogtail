#!/usr/bin/python3
"""
Unit tests for the dogtail.tree Node Selection.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402

# TODO revisit what these are needed for.
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import unittest

from dogtail.rawinput import pressKey

try:
    from tests.gtk_demo_test import Gtk3DemoTest
except ImportError:
    from gtk_demo_test import Gtk3DemoTest


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
        pressKey("+")
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

        # Weird way to do this but it works as a unit test.
        self.demo.child("Icon View").click()
        pressKey("+")
        self.run_demo("Icon View Basics")

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
        pressKey("+")
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
        pressKey("+")
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
