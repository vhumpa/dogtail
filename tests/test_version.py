#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import dogtail.version

"""
Unit tests for the dogtail.version module
"""


class TestVersion(unittest.TestCase):
    def test_version_from_string_list(self):
        version_instance = dogtail.version.Version([1, 2, 3])
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_from_string(self):
        version_instance = dogtail.version.Version("1.2.3")
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_from_string_dedicated(self):
        version_instance = dogtail.version.Version.fromString("1.2.3")
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_less_than(self):
        version = dogtail.version.Version.fromString("1.2.3")
        version_less1 = dogtail.version.Version.fromString("1.2.2")
        version_less2 = dogtail.version.Version.fromString("1.1.3")
        version_less3 = dogtail.version.Version.fromString("0.8.3")
        self.assertTrue(version_less1 < version)
        self.assertTrue(version_less2 < version)
        self.assertTrue(version_less3 < version)
        self.assertTrue(version_less1 <= version)
        self.assertTrue(version_less2 <= version)
        self.assertTrue(version_less3 <= version)


    def test_version_more_than(self):
        version = dogtail.version.Version.fromString("1.2.3")
        version_less1 = dogtail.version.Version.fromString("1.2.2")
        version_less2 = dogtail.version.Version.fromString("1.1.3")
        version_less3 = dogtail.version.Version.fromString("0.8.3")
        self.assertTrue(version > version_less1)
        self.assertTrue(version > version_less2)
        self.assertTrue(version > version_less3)
        self.assertTrue(version >= version_less1)
        self.assertTrue(version >= version_less2)
        self.assertTrue(version >= version_less3)


    def test_version_equals(self):
        version0 = dogtail.version.Version([1, 2, 3])
        version1 = dogtail.version.Version.fromString("1.2.3")
        version2 = dogtail.version.Version.fromString("1.2.2")
        self.assertTrue(version0 == version1)
        self.assertFalse(version0 == version2)
        self.assertFalse(version1 == version2)
        self.assertTrue(version0 >= version1)
        self.assertTrue(version0 <= version1)
        self.assertTrue(version0 >= version2)
        self.assertFalse(version0 <= version2)
        self.assertTrue(version1 >= version2)
        self.assertFalse(version1 <= version2)
        self.assertFalse(version0 != version1)
        self.assertFalse(version1 != version0)
        self.assertTrue(version2 != version0)
        self.assertTrue(version2 != version1)
