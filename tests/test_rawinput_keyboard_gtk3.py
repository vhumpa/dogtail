#!/usr/bin/python3
"""
Unit tests for the dogtail.rawinput keyboard methods.
"""

# pylint: disable=import-outside-toplevel


import os
from time import sleep

import unittest

try:
    from tests.test_gtk_demo import Gtk3DemoTest
except ImportError:
    from test_gtk_demo import Gtk3DemoTest

from dogtail.rawinput import (
    press_key,
    key_combo,
    type_text,
)


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk3-demo"), "Skipping, no gtk3-demo.")
class TestGtk3DemoRawinputKeyboard(Gtk3DemoTest):
    """
    Class to test dogtail's rawinput keyboard methods.
    """


    def test_press_key(self):
        """
        Testing press key.
        """

        press_key("Esc")
        sleep(1)

        press_key("Super")
        sleep(1)

        press_key("Esc")
        sleep(1)


    def test_press_key_no_such_key(self):
        """
        Testing press key with no such key.
        """

        with self.assertRaises(KeyError):
            press_key("No such key.")


    def test_key_combo_simple(self):
        """
        Testing simple key combo.
        """

        key_combo("<End>")
        self.assertTrue(self.demo.child("Tree View").showing)


    def test_key_combo_multi_key(self):
        """
        Testing simple key combo with multiple keys.
        """

        press_key("Esc")
        sleep(1)

        self.run_demo("Clipboard")

        clipboard_window = self.demo.find_children(
            lambda x: x.name == "Clipboard" and x.role_name == "frame"
        )[-1]

        text_field = clipboard_window.child(role_name="text")
        text_field.text = "testing "

        key_combo("<Ctrl><A>")
        sleep(0.2)

        key_combo("<Ctrl><C>")
        sleep(0.2)

        key_combo("<Ctrl><V>")
        sleep(0.2)

        key_combo("<Ctrl><V>")
        sleep(0.2)

        self.assertEqual(text_field.text, "testing testing ")


    def test_key_combo_wrong_key(self):
        """
        Testing key combo with wrong key.
        """

        with self.assertRaises(ValueError):
            key_combo("<Not_defined_key>")


    def test_type_text(self):
        """
        Testing type text.
        """

        press_key("Esc")
        sleep(1)

        self.run_demo("Clipboard")

        clipboard_window = self.demo.find_children(
            lambda x: x.name == "Clipboard" and x.role_name == "frame"
        )[-1]

        text_field = clipboard_window.child(role_name="text")
        text_field.click()

        type_text("testing type text")
        sleep(1)

        copy_button = clipboard_window.child("Copy")
        copy_button.click()

        paste_button = clipboard_window.child("Paste")
        paste_button.click()

        number_of_text_fields = self.demo.find_children(
            lambda x:
            (x.text == "testing type text") or
            (x.name == "testing type text" and x.role_name == "label")
        )

        self.assertEqual(len(number_of_text_fields), 2)


if __name__ == "__main__":
    unittest.main()
