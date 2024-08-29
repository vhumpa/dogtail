#!/usr/bin/python3
"""
Unit tests for the dogtail.utils run.
"""

# TODO revisit what these are needed for.
from __future__ import absolute_import, division, print_function, unicode_literals

from time import sleep

import os
import signal

import unittest
from dogtail.utils import run
from dogtail.tree import root


class TestRun(unittest.TestCase):
    """
    Class to test dogtail's utils run method.
    """

    def setUp(self):
        self.pid = None


    def tearDown(self):

        if self.pid:
            os.kill(self.pid, signal.SIGKILL)

        os.system('killall gtk3-demo-application > /dev/null 2>&1')
        os.system('killall gtk3-demo > /dev/null 2>&1')

        # Sleep just enough to let the app actually die.
        # AT-SPI doesn't like being hammered too fast.

        sleep(0.5)


    def test_run(self):
        """
        Test utils run function.
        """

        self.pid = run("gtk3-demo")
        self.assertIsNotNone(root.application("gtk3-demo"))


    def test_run_incorrect(self):
        """
        Test utils run function on incorrect script.
        """

        self.pid = None
        with self.assertRaises(OSError):
            self.pid = run("gtk3-not-existing-demo")


    def test_run_dumb(self):
        """
        Test utils run function with dumb parameter to not check start up.
        """

        self.pid = run("gtk3-demo", dumb=True)
        self.assertIsNotNone(root.application("gtk3-demo"))


if __name__ == "__main__":
    unittest.main()
