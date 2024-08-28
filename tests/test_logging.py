#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import dogtail.tree
from gtkdemotest import trap_stdout
import unittest

"""
Unit tests for the dogtail.logging package
"""


class TestLogging(unittest.TestCase):

    def setUp(self):
        self.old_log_dir = dogtail.config.config.logDir

    def tearDown(self):
        dogtail.config.config.logDebugToFile = False
        dogtail.config.config.logDir = self.old_log_dir

    def test_entryStamp_is_not_empty(self):
        ts = dogtail.logging.TimeStamp()
        self.assertEqual(len(ts.entryStamp()) > 0, True)

    def test_correct_error_if_log_dir_does_not_exist(self):
        import shutil
        dogtail.logging.Logger(logName="test_logging").createFile()
        shutil.rmtree(dogtail.config.config.logDir)
        self.assertRaises(OSError, dogtail.logging.Logger, "log", file=True)

    def test_unique_name(self):
        logger1 = dogtail.logging.Logger("log", file=True)
        logger1.createFile()
        logger2 = dogtail.logging.Logger("log", file=True)
        logger2.createFile()
        logger3 = dogtail.logging.Logger("log", file=True)
        self.assertNotEqual(logger1.fileName, logger2.fileName)
        self.assertNotEqual(logger2.fileName, logger3.fileName)

    def test_no_new_line_to_file(self):
        dogtail.config.config.logDebugToFile = True
        logger = dogtail.logging.Logger("log", file=True, stdOut=False)
        logger.log("hello world", newline=False)
        with open(logger.fileName, 'r') as f:
            logger_text = f.read()
        self.assertTrue("hello world " in logger_text)

    def test_no_new_line_to_stdout(self):
        dogtail.config.config.logDebugToFile = False
        logger = dogtail.logging.Logger("log", file=False, stdOut=True)
        output = trap_stdout(
            logger.log, {'message': 'hello world', 'newline': False})
        self.assertEqual(output, "hello world")

    def test_no_new_line_to_both_file_and_stdout(self):
        dogtail.config.config.logDebugToFile = True
        logger = dogtail.logging.Logger("log", file=True, stdOut=True)
        output = trap_stdout(
            logger.log, {'message': 'hello world', 'newline': False})
        self.assertTrue("hello world" in output)
        with open(logger.fileName, 'r') as f:
            logger_text = f.read()
        self.assertTrue("hello world " in logger_text)

    def test_force_to_file(self):
        dogtail.config.config.logDebugToFile = False
        logger = dogtail.logging.Logger("log", file=True, stdOut=False)
        logger.log("hello world", force=True)
        with open(logger.fileName, 'r') as f:
            logger_text = f.read()
        self.assertTrue("hello world" in logger_text)

    def test_results_logger_correct_dict(self):
        logger = dogtail.logging.ResultsLogger("log")
        output = trap_stdout(logger.log, {'entry': {'a': '1'}})
        self.assertEqual('a:      1' in output, True)

    def test_results_logger_incorrect_dict(self):
        logger = dogtail.logging.ResultsLogger("log")
        self.assertRaises(ValueError, logger.log, "not a dict")
