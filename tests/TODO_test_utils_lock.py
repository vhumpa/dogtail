#!/usr/bin/python3
"""
Unit tests for the dogtail.utils accessibility.
"""

# TODO revisit what these are needed for.
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

#TODO
class TestLock(unittest.TestCase):
    def tearDown(self):
        os.system("rm -rf /tmp/dogtail-test.lock*")


    def test_set_unrandomized_lock(self):
        test_lock = dogtail.utils.Lock(lockname='dogtail-test.lock', randomize=False)
        self.assertEqual(test_lock.lockdir, "/tmp/dogtail-test.lock")
        self.assertFalse(os.path.isdir(test_lock.lockdir))
        test_lock.lock()
        self.assertTrue(os.path.isdir(test_lock.lockdir))
        test_lock.unlock()
        self.assertFalse(os.path.isdir(test_lock.lockdir))


    def test_double_lock(self):
        test_lock = dogtail.utils.Lock(lockname='dogtail-test.lock', randomize=False, unlockOnExit=True)
        test_lock.lock()
        with self.assertRaises(OSError):
            test_lock.lock()


    def test_double_unlock(self):
        test_lock = dogtail.utils.Lock(lockname='dogtail-test.lock', randomize=False)
        test_lock.lock()
        test_lock.unlock()
        with self.assertRaises(OSError):
            test_lock.unlock()


    def test_randomize(self):
        test_lock = dogtail.utils.Lock(lockname='dogtail-test.lock', randomize=True)
        self.assertIn("/tmp/dogtail-test.lock", test_lock.lockdir)
        self.assertFalse(os.path.isdir(test_lock.lockdir))
        test_lock.lock()
        self.assertTrue(os.path.isdir(test_lock.lockdir))
        test_lock.unlock()
        self.assertFalse(os.path.isdir(test_lock.lockdir))
