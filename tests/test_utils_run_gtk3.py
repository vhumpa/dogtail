#!/usr/bin/python3
"""
Unit tests for the dogtail.utils run.
"""


from time import sleep

import os

import unittest
from dogtail.utils import run
from dogtail.tree import root


@unittest.skipIf(not os.path.isfile("/usr/bin/gtk3-demo"), "Skipping, no gtk3-demo.")
class TestGtk3Run(unittest.TestCase):
    """
    Class to test dogtail's utils run method.
    """

    def setUp(self):
        self.process = None


    def tearDown(self):

        if self.process:
            self.process.kill()
            self.process.wait()

        os.system('killall gtk3-demo-application > /dev/null 2>&1')

        # Sleep just enough to let the app actually die.
        # AT-SPI doesn't like being hammered too fast.

        sleep(0.5)


    def test_run(self):
        """
        Test utils run function.
        """

        self.process = run("gtk3-demo")
        self.assertIsNotNone(root.application("gtk3-demo"))


    def test_run_incorrect(self):
        """
        Test utils run function on incorrect script.
        """

        self.process = None
        with self.assertRaises(OSError):
            self.process = run("gtk3-not-existing-demo")


    def test_run_dumb(self):
        """
        Test utils run function with dumb parameter to not check start up.
        """

        self.process = run("gtk3-demo", dumb=True)
        self.assertIsNotNone(root.application("gtk3-demo"))


if __name__ == "__main__":
    unittest.main()
