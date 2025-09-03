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

try:
    from tests.test_gtk_demo import Gtk4DemoTest
except ImportError:
    from test_gtk_demo import Gtk4DemoTest


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk4-demo"), "Skipping, no gtk4-demo.")
class TestGtk4DogtailNodeSelection(Gtk4DemoTest):
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


    # Not working in gtk4-demo.
    @unittest.SkipTest
    def test_select(self):
        """
        Testing select.
        """

        # Weird way to do this but it works as a unit test.
        scroll_bar = self.demo.child(role_name="scroll bar")
        for _ in range(50):
            scroll_bar.value += 100
            try:
                icon_view = self.demo.child("Icon View Basics", retry=False)
                icon_view.double_click()
                break
            except RuntimeError:
                pass

        window = self.demo.find_children(
            lambda x: x.name == "Icon View Basics" and
            x.role_name == "frame"
        )[-1]

        layered_pane = window.child(role_name="layered pane")

        self.assertFalse(layered_pane.children[1].selected)
        layered_pane.children[1].select()
        self.assertTrue(layered_pane.children[1].selected)


    # Not working in gtk4-demo.
    @unittest.SkipTest
    def test_deselect(self):
        """
        Testing deselect.
        """

        # Weird way to do this but it works as a unit test.
        scroll_bar = self.demo.child(role_name="scroll bar")
        for _ in range(50):
            scroll_bar.value += 100
            try:
                icon_view = self.demo.child("Icon View Basics", retry=False)
                icon_view.double_click()
                break
            except RuntimeError:
                pass

        window = self.demo.find_children(
            lambda x: x.name == "Icon View Basics" and
            x.role_name == "frame"
        )[-1]

        layered_pane = window.child(role_name="layered pane")

        layered_pane.children[1].select()
        self.assertTrue(layered_pane.children[1].selected)

        layered_pane.children[1].deselect()
        self.assertFalse(layered_pane.children[1].selected)


    # Not working in gtk4-demo.
    @unittest.SkipTest
    def test_select_all(self):
        """
        Testing select all.
        """

        # Weird way to do this but it works as a unit test.
        scroll_bar = self.demo.child(role_name="scroll bar")
        for _ in range(50):
            scroll_bar.value += 100
            try:
                icon_view = self.demo.child("Icon View Basics", retry=False)
                icon_view.double_click()
                break
            except RuntimeError:
                pass

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


    # Not working in gtk4-demo.
    @unittest.SkipTest
    def test_deselect_all(self):
        """
        Testing deselect all.
        """

        # Weird way to do this but it works as a unit test.
        scroll_bar = self.demo.child(role_name="scroll bar")
        for _ in range(50):
            scroll_bar.value += 100
            try:
                icon_view = self.demo.child("Icon View Basics", retry=False)
                icon_view.double_click()
                break
            except RuntimeError:
                pass

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
