#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import dogtail.predicate
import dogtail.tree
import dogtail.i18n
import os.path
import dogtail.config
import dogtail.version
import dogtail.utils
from gtkdemotest import GtkDemoTest, trap_stdout
import unittest
import time

"""
Unit tests for the dogtail.procedural API
"""

__author__ = "Zack Cerza <zcerza@redhat.com>"

dogtail.config.config.logDebugToFile = False
dogtail.config.config.logDebugToStdOut = True


class TestScreenshot(GtkDemoTest):
    def make_expected_and_compare(self, actual_path, jpg_tolerance=None):
        extension = actual_path.split('.')[-1]
        expected_path = actual_path.replace(extension, "expected." + extension)

        import os
        os.system("gnome-screenshot -f %s" % expected_path)

        command = ["compare", "-metric", "MAE",
                   actual_path, expected_path, "output"]
        import subprocess
        p = subprocess.Popen(command, stderr=subprocess.PIPE)
        output, error = p.communicate()

        import re
        m = re.search(r"\((.*)\)", str(error))
        self.assertTrue(0.1 >= float(m.group(1)))


    def test_screenshot_incorrect_timestamp(self):
        self.assertRaises(TypeError, dogtail.utils.screenshot, "timeStamp", None)


    def test_screenshot_default(self):
        actual_path = dogtail.utils.screenshot()
        self.make_expected_and_compare(actual_path)


    def test_screenshot_basename(self):
        actual_path = dogtail.utils.screenshot("basename")
        self.make_expected_and_compare(actual_path)


    def test_screenshot_no_time_stamp(self):
        actual_path = dogtail.utils.screenshot(timeStamp=False)
        self.make_expected_and_compare(actual_path)


    def test_screenshot_jpeg(self):
        actual_path = dogtail.utils.screenshot("basename.jpg")
        self.make_expected_and_compare(actual_path, jpg_tolerance=True)


    def test_screenshot_unknown_format(self):
        self.assertRaises(ValueError, dogtail.utils.screenshot, "basename.dat")


class TestRun(unittest.TestCase):
    def setUp(self):
        self.pid = None


    def tearDown(self):
        import os
        import signal
        if self.pid:
            os.kill(self.pid, signal.SIGKILL)
        os.system('killall gtk3-demo-application > /dev/null 2>&1')
        os.system('killall gtk3-demo-appli > /dev/null 2>&1')
        # Sleep just enough to let the app actually die.
        # AT-SPI doesn't like being hammered too fast.
        time.sleep(0.5)


    def test_run(self):
        self.pid = dogtail.utils.run('gtk3-demo')
        dogtail.tree.root.application('gtk3-demo')


    def test_run_wrong(self):
        self.pid = None
        with self.assertRaises(OSError):
            self.pid = dogtail.utils.run('gtk3-virtual-nonexisting-demo')


    def test_run_dumb(self):
        self.pid = dogtail.utils.run('gtk3-demo', dumb=True)
        dogtail.tree.root.application('gtk3-demo')


class TestDelay(unittest.TestCase):
    def test_doDelay_implicit(self):
        dogtail.utils.config.defaultDelay = 2.0
        start = time.time()
        dogtail.utils.doDelay()
        self.assertTrue(time.time() - start >= 2.0)


    def test_doDelay_explicit(self):
        dogtail.utils.config.defaultDelay = 1.0
        start = time.time()
        dogtail.utils.doDelay(2.0)
        self.assertTrue(time.time() - start >= 2.0)


    def test_doDelay_logger(self):
        dogtail.utils.config.defaultDelay = 2.0
        dogtail.utils.config.debugSleep = True
        output = trap_stdout(dogtail.utils.doDelay).split()
        self.assertEqual(len(output), 3)
        self.assertEqual(float(output[2]), 2.0)
        dogtail.utils.config.debugSleep = False


class TestA11Y(unittest.TestCase):
    def test_bail_when_a11y_disabled(self):
        self.assertRaises(SystemExit, dogtail.utils.bailBecauseA11yIsDisabled)


    def test_enable_a11y(self):
        dogtail.utils.enableA11y()


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


class TestI18N(unittest.TestCase):
    def test_load_all_translations_for_language(self):
        dogtail.i18n.loadAllTranslationsForLanguage('en_US')
