#!/usr/bin/python3
"""
Unit tests for the dogtail.utils Lock.
"""

# ruff: noqa: E501


import unittest

import os

from dogtail.utils import Lock


class TestLock(unittest.TestCase):
    """
    Class to test dogtail's utils Lock Class.
    """

    def tearDown(self):
        os.system("rm -rf /tmp/dogtail-test.lock*")


    def test_set_not_randomized_lock(self):
        """
        Test utils Lock not randomized lock.
        """

        test_lock = Lock(lockname="dogtail-test.lock", randomize=False)
        self.assertEqual(test_lock.lockdir, "/tmp/dogtail-test.lock")
        self.assertFalse(os.path.isdir(test_lock.lockdir))
        test_lock.lock()
        self.assertTrue(os.path.isdir(test_lock.lockdir))
        test_lock.unlock()
        self.assertFalse(os.path.isdir(test_lock.lockdir))


    def test_double_lock(self):
        """
        Test utils Lock double locked.
        """

        test_lock = Lock(lockname="dogtail-test.lock", randomize=False, unlock_on_exit=True)
        test_lock.lock()
        with self.assertRaises(OSError):
            test_lock.lock()


    def test_double_lock_original_parameter(self):
        """
        Test utils Lock double locked with original parameter.
        """

        test_lock = Lock(lockname="dogtail-test.lock", randomize=False, unlockOnExit=True)
        test_lock.lock()
        with self.assertRaises(OSError):
            test_lock.lock()


    def test_double_unlock(self):
        """
        Test utils Lock double unlock.
        """

        test_lock = Lock(lockname="dogtail-test.lock", randomize=False)
        test_lock.lock()
        test_lock.unlock()
        with self.assertRaises(OSError):
            test_lock.unlock()


    def test_randomize(self):
        """
        Test utils Lock randomized lock.
        """

        test_lock = Lock(lockname="dogtail-test.lock", randomize=True)
        self.assertIn("/tmp/dogtail-test.lock", test_lock.lockdir)
        self.assertFalse(os.path.isdir(test_lock.lockdir))
        test_lock.lock()
        self.assertTrue(os.path.isdir(test_lock.lockdir))
        test_lock.unlock()
        self.assertFalse(os.path.isdir(test_lock.lockdir))
