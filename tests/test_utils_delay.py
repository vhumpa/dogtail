#!/usr/bin/python3
"""
Unit tests for the dogtail.utils delays.
"""


import os
from time import time

import unittest

from dogtail.utils import do_delay
from dogtail.config import config


class TestDelay(unittest.TestCase):
    """
    Class to test dogtail's utils do_delay method.
    """

    def test_do_delay_implicit(self):
        """
        Test utils do_delay function by setting config value.
        """

        config.default_delay = 2.0
        start_time = time()
        do_delay()
        self.assertTrue(time() - start_time >= 2.0)


    def test_do_delay_explicit(self):
        """
        Test utils do_delay function by passing value to the method.
        """

        config.default_delay = 2.0
        start_time = time()
        do_delay(2.0)
        self.assertTrue(time() - start_time >= 2.0)


    def test_do_delay_debug_sleep(self):
        """
        Test utils do_delay function with debug_sleep option.
        """

        config.default_delay = 2.0
        config.debug_sleep = True
        start_time = time()
        do_delay(2.0)

        self.assertTrue(os.path.isfile(config.debug_file))

        with open(config.debug_file, "r", encoding="utf-8") as _f:
            file_content = _f.read()
            self.assertTrue("Debug Sleep: " in file_content)

        self.assertTrue(time() - start_time >= 2.0)


if __name__ == "__main__":
    unittest.main()
