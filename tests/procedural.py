#!/usr/bin/python
"""
Unit tests for the dogtail.procedural API
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

import unittest
from dogtail.procedural import *
config.logDebugToFile = False
config.logDebugToStdOut = False
import Node

class GtkDemoTest(Node.GtkDemoTest):
    def setUp(self):
        self.pid = run('gtk-demo')
        self.app = focus.application.node

    #FIXME: Implement doubleclick() in d.procedural and override the other 
    # methods of Node.GtkDemoTest


class TestFocusApplication(GtkDemoTest):
    
    # FIXME: Should the following pass? Design decision.
    #def testFocusingBogusName(self):
    #    focus.application("should not be found")
    #    self.assertEquals(focus.application.node, None)

    def testFocusingBasic(self):
        "Ensure that focus.application() sets focus.application.node properly"
        focus.application("gtk-demo")
        self.assertEquals(focus.application.node, self.app)


class TestFocusWidget(GtkDemoTest):
    def testFocusingBogusName(self):
        focus.widget("should not be found")
        self.assertEquals(focus.widget.node, None)

    def testFocusingBasic(self):
        "Ensure that focus.widget('foo') finds a node with name 'foo'"
        focus.widget("Application main window")
        self.assertEquals(focus.widget.name, "Application main window")


class TestFocusWindow(GtkDemoTest):
    def testFocusingBogusName(self):
        focus.window("should not be found")
        self.assertEquals(focus.window.node, None)


class TestFocusDialog(GtkDemoTest):
    def testFocusingBogusName(self):
        focus.dialog("should not be found")
        self.assertEquals(focus.dialog.node, None)


class TestFocusBase(GtkDemoTest):
    def testFocusingApp(self):
        "Ensure that focus.app() works like focus.application()"
        focus.app('gtk-demo')
        self.assertEquals(focus.app.node, self.app)


if __name__ == "__main__":
    unittest.main()
