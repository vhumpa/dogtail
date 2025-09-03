#!/usr/bin/python3
"""
Unit tests for the dogtail.tree Node Search.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402


import os
import unittest

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from dogtail.predicate import GenericPredicate

try:
    from tests.test_gtk_demo import Gtk4DemoTest
except ImportError:
    from test_gtk_demo import Gtk4DemoTest


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk4-demo"), "Skipping, no gtk4-demo.")
class TestDogtailNodeSearch(Gtk4DemoTest):
    """
    Class to test dogtail's Node Search.
    """

    def test_child(self):
        """
        Testing child.
        """

        child_result = self.demo.child("Info")
        self.assertIsNotNone(child_result)
        self.assertIsInstance(child_result, Atspi.Accessible)


    def test_find_child(self):
        """
        Testing find child.
        """

        find_child_result = self.demo.find_child(lambda x: x.name == "Info")
        self.assertIsNotNone(find_child_result)
        self.assertIsInstance(find_child_result, Atspi.Accessible)


    def test_find_children(self):
        """
        Testing find children.
        """

        find_children_result = self.demo.find_children(lambda x: x.name == "Info")
        self.assertIsNotNone(self.demo.find_children(lambda x: x.name == "Info"))
        self.assertIsInstance(find_children_result, list)


    def test_find_child_with_predicate(self):
        """
        Testing find child with predicate.
        """

        find_child_result = self.demo.find_child(GenericPredicate(name="Info"))
        self.assertIsNotNone(find_child_result)
        self.assertIsInstance(find_child_result, Atspi.Accessible)


    def test_find_children_with_predicate(self):
        """
        Testing find children with predicate.
        """

        find_children_result = self.demo.find_children(
            GenericPredicate(name="Info")
        )
        self.assertIsNotNone(find_children_result)
        self.assertIsInstance(find_children_result, list)


    def test_find_ancestor(self):
        """
        Testing find ancestor.
        """

        find_ancestor_result = self.demo.children[0].find_ancestor(
            lambda x: x.role_name == "application"
        )
        self.assertIsNotNone(find_ancestor_result)
        self.assertIsInstance(find_ancestor_result, Atspi.Accessible)


    def test_is_child(self):
        """
        Testing is child.
        """

        child_name = self.demo.children[0].name
        child_role_name = self.demo.children[0].role_name

        is_child_result = self.demo.is_child(child_name, child_role_name)
        self.assertEqual(is_child_result, True)
        self.assertIsInstance(is_child_result, bool)


if __name__ == "__main__":
    unittest.main()
