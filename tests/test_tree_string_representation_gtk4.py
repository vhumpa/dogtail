#!/usr/bin/python3
"""
Unit tests for the dogtail.tree Node String Representation.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402


import os
import unittest

try:
    from tests.test_gtk_demo import Gtk4DemoTest, trap_stdout
except ImportError:
    from test_gtk_demo import Gtk4DemoTest, trap_stdout


SOURCE_DUMP_STRING = """[ 'Source' | 'page tab' | '' ]
  [ 'Source' | 'label' | '' ]"""

SOURCE_TREE_STRING = """└──[ 'Source' | 'page tab' | '' ]
     └──[ 'Source' | 'label' | '' ]"""


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk4-demo"), "Skipping, no gtk4-demo.")
class TestGtk4DogtailNodeValue(Gtk4DemoTest):
    """
    Class to test dogtail's Node String Representation.
    """

    def test_dump_representation(self):
        """
        Testing dump string.
        """

        source_node = self.demo.child("Source")

        source_node_dump_output = trap_stdout(source_node.dump)
        self.assertEqual(source_node_dump_output, SOURCE_DUMP_STRING)


    def test_tree_representation(self):
        """
        Testing tree string.
        """

        source_node = self.demo.child("Source")

        source_node_tree_output = trap_stdout(source_node.tree)
        self.assertEqual(source_node_tree_output, SOURCE_TREE_STRING)


if __name__ == "__main__":
    unittest.main()
