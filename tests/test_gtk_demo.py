#!/usr/bin/python3
"""
Useful classes for in session manipulation with applications.
"""


import os
import sys

from io import StringIO

from time import sleep

import unittest
import dogtail.utils


class Gtk3DemoTest(unittest.TestCase):
    """
    Instances of the TestCase class represent the logical test units in the unittest
    universe. This class is intended to be used as a base class, with specific tests
    being implemented by concrete subclasses. This class implements the interface needed
    by the test runner to allow it to drive the tests, and methods that the test code
    can use to check for and report various kinds of failure.
    """

    # To make this functional we have to override the setUp method in camelCase.
    def setUp(self):
        """
        Method called to prepare the test fixture. This is called immediately before
        calling the test method
        """

        self.process = dogtail.utils.run("gtk3-demo")

        # Let time application start properly.
        sleep(1)

        self.demo = dogtail.tree.root.application("gtk3-demo")


    # To make this functional we have to override the tearDown method in camelCase.
    def tearDown(self):
        """
        Method called immediately after the test method has been called and the result
        recorded
        """

        self.process.kill()
        self.process.wait()

        # This one can be started in test, kill it after gtk3-demo too.
        os.system("killall gtk3-demo-application > /dev/null 2>&1")

        # Sleep just enough to let the app actually die.
        # AT-SPI doesn't like being hammered too fast.

        sleep(1)


    def run_demo(self, demo_name, retry=True):
        """
        Activate the named demo within the gtk3-demo app.
        """

        tree = self.demo.child(roleName="tree table")
        tree.child(demo_name, retry=retry).do_action_named("activate")


class Gtk4DemoTest(unittest.TestCase):
    """
    Instances of the TestCase class represent the logical test units in the unittest
    universe. This class is intended to be used as a base class, with specific tests
    being implemented by concrete subclasses. This class implements the interface needed
    by the test runner to allow it to drive the tests, and methods that the test code
    can use to check for and report various kinds of failure.
    """

    def setUp(self):
        """
        Method called to prepare the test fixture. This is called immediately before
        calling the test method
        """

        self.process = dogtail.utils.run("gtk4-demo")

        # Let time application start properly.
        sleep(1)

        self.demo = dogtail.tree.root.application("gtk4-demo")


    def tearDown(self):
        """
        Method called immediately after the test method has been called and the result
        recorded
        """

        self.process.kill()
        self.process.wait()

        # This one can be started in test, kill it after gtk3-demo too.
        os.system("killall gtk4-demo-application > /dev/null 2>&1")

        # Sleep just enough to let the app actually die.
        # AT-SPI doesn't like being hammered too fast.

        sleep(1)


    def run_demo(self, demo_name, retry=True):
        """
        Activate the named demo within the gtk3-demo app.
        """

        tree = self.demo.child(roleName="tree table")
        tree.child(demo_name, retry=retry).do_action_named("activate")


def trap_stdout(function, args=None):
    """
    Grab stdout output during function execution.
    """

    saved_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out
        if isinstance(args, dict):
            function(**args)
        elif args:
            function(args)
        else:
            function()
        output = out.getvalue().strip()
    finally:
        sys.stdout = saved_stdout
    return output
