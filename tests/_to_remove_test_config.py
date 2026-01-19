#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
import dogtail.config

"""
Unit tests for the dogtail.config class
"""


class TestConfiguration(unittest.TestCase):

    def test_get_set_all_properties(self):
        for option in list(dogtail.config.config.defaults.keys()):
            print("Setting config.%s property" % str(option))
            old_value = dogtail.config.config.__getattr__(option)
            value = ''
            if 'Dir' in option:
                value = '/tmp/dogtail/'  # Special value for dir-related properties
            dogtail.config.config.__setattr__(option, value)
            self.assertEqual(dogtail.config.config.__getattr__(option), value)
            dogtail.config.config.__setattr__(option, old_value)

    def test_default_directories_created(self):
        import os.path
        self.assertEqual(
            os.path.isdir(dogtail.config.config.scratchDir), True)
        self.assertEqual(os.path.isdir(dogtail.config.config.logDir), True)
        self.assertEqual(os.path.isdir(dogtail.config.config.dataDir), True)

    def test_set(self):
        self.assertRaises(AttributeError, setattr, dogtail.config.config, 'nosuchoption', 42)

    def test_get(self):
        self.assertRaises(AttributeError, getattr, dogtail.config.config, 'nosuchoption')

    def helper_create_directory_and_set_option(self, path, property_name):
        import os.path
        if os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        dogtail.config.config.__setattr__(property_name, path)
        self.assertEqual(os.path.isdir(path), True)

    def test_create_scratch_directory(self):
        new_folder = "/tmp/dt"
        self.helper_create_directory_and_set_option(new_folder, 'scratchDir')

    def test_create_data_directory(self):
        new_folder = "/tmp/dt_data"
        self.helper_create_directory_and_set_option(new_folder, 'dataDir')

    def test_create_log_directory(self):
        new_folder = "/tmp/dt_log"
        self.helper_create_directory_and_set_option(new_folder, 'logDir')

    def test_load(self):
        dogtail.config.config.load({'actionDelay': 2.0})
        self.assertEqual(dogtail.config.config.actionDelay, 2.0)

    def test_reset(self):
        default_actionDelay = dogtail.config.config.defaults['actionDelay']
        dogtail.config.config.actionDelay = 2.0
        dogtail.config.config.reset()
        self.assertEqual(dogtail.config.config.actionDelay, default_actionDelay)
