#!/usr/bin/python3
"""
Unit tests for the dogtail.rawinput mouse buttons.
"""

# pylint: disable=import-outside-toplevel


import os
import unittest

from time import sleep

try:
    from tests.test_gtk_demo import Gtk3DemoTest
except ImportError:
    from test_gtk_demo import Gtk3DemoTest

from dogtail.rawinput import (
    click,
    double_click,
    press,
    release,
    press_key
)


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk3-demo"), "Skipping, no gtk3-demo.")
class TestGtk3DemoRawinputMouse(Gtk3DemoTest):
    """
    Class to test dogtail's rawinput mouse buttons.
    """


    def test_click_in_demo(self):
        """
        Testing click.
        """

        press_key("Esc")
        sleep(1)

        builder_button = self.demo.child("Builder")
        self.assertFalse(builder_button.focused)

        click(*builder_button.center)
        sleep(1)
        self.assertTrue(builder_button.focused)


    def test_double_click_in_demo(self):
        """
        Testing double_click.
        """

        press_key("Esc")
        sleep(1)

        builder_button = self.demo.child("Builder")

        # At first it is not focused so the frame is named differently.
        self.assertEqual(len([x for x in self.demo.children if x.name == "Builder"]), 0)

        # Upon clicking the Builder will appear in the main frame too.
        click(*builder_button.center)
        self.assertEqual(len([x for x in self.demo.children if x.name == "Builder"]), 1)

        double_click(*builder_button.center)

        # Upon double click the new frame will open with the same name.
        self.assertEqual(len([x for x in self.demo.children if x.name == "Builder"]), 2)


    def test_press_release_in_demo(self):
        """
        Testing press and release.
        """

        press_key("Esc")
        sleep(1)

        self.run_demo("Builder")

        save_button = self.demo.child("Save", showing_only=True)
        self.assertFalse(save_button.armed)

        press(*save_button.center)
        self.assertTrue(save_button.armed)

        release(*save_button.center)
        self.assertFalse(save_button.armed)


if __name__ == "__main__":
    unittest.main()
