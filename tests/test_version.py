#!/usr/bin/python3
"""
Unit tests for the dogtail.version module.
"""

# pylint: disable=line-too-long
# ruff: noqa: E501


import unittest
import dogtail.version


class TestVersion(unittest.TestCase):
    """
    Class to test dogtail's version methods.
    """

    def test_version_from_string_list(self):
        """
        Tests for Version using a list.
        """

        version_instance = dogtail.version.Version([1, 2, 3])
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_from_string(self):
        """
        Tests for Version using a string.
        """

        version_instance = dogtail.version.Version("1.2.3")
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_from_string_compatibility_method(self):
        """
        Tests for Version using a fromString function.
        """

        version_instance = dogtail.version.Version.fromString("1.2.3")
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_from_string_method(self):
        """
        Tests for Version using a from_string function.
        """

        version_instance = dogtail.version.Version.from_string("1.2.3")
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_less_than(self):
        """
        Tests for Version matching less than values.
        """

        version_base = dogtail.version.Version.from_string("1.2.3")

        version_less_z = dogtail.version.Version.from_string("1.2.2")
        version_less_y = dogtail.version.Version.from_string("1.1.3")
        version_less_x = dogtail.version.Version.from_string("0.2.3")

        self.assertTrue(version_less_z < version_base)
        self.assertTrue(version_less_y < version_base)
        self.assertTrue(version_less_x < version_base)

        self.assertTrue(version_less_z <= version_base)
        self.assertTrue(version_less_y <= version_base)
        self.assertTrue(version_less_x <= version_base)


    def test_version_more_than(self):
        """
        Tests for Version matching less than values.
        """

        version_base = dogtail.version.Version.from_string("1.2.3")

        version_less_z = dogtail.version.Version.from_string("1.2.2")
        version_less_y = dogtail.version.Version.from_string("1.1.3")
        version_less_x = dogtail.version.Version.from_string("0.2.3")

        self.assertTrue(version_base > version_less_z)
        self.assertTrue(version_base > version_less_y)
        self.assertTrue(version_base > version_less_x)

        self.assertTrue(version_base >= version_less_z)
        self.assertTrue(version_base >= version_less_y)
        self.assertTrue(version_base >= version_less_x)


    def test_version_equals(self):
        """
        Tests for Version matching equal values.
        """

        version_base = dogtail.version.Version([1, 2, 3])
        version_equal = dogtail.version.Version.from_string("1.2.3")
        version_not_equal = dogtail.version.Version.from_string("1.2.2")

        self.assertTrue(version_base == version_equal)
        self.assertFalse(version_base == version_not_equal)
        self.assertFalse(version_equal == version_not_equal)

        self.assertTrue(version_base >= version_equal)
        self.assertTrue(version_base <= version_equal)
        self.assertTrue(version_base >= version_not_equal)

        self.assertFalse(version_base <= version_not_equal)
        self.assertTrue(version_equal >= version_not_equal)
        self.assertFalse(version_equal <= version_not_equal)

        self.assertFalse(version_base != version_equal)
        self.assertFalse(version_equal != version_base)
        self.assertTrue(version_not_equal != version_base)
        self.assertTrue(version_not_equal != version_equal)


    def test_version_constructor_new(self):
        """
        Tests for Version constructor snake case value.
        """

        version_instance = dogtail.version.Version(version_list=[1, 2, 3])
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_constructor_old(self):
        """
        Tests for Version constructor camelCase value.
        """

        version_instance = dogtail.version.Version(versionList=[1, 2, 3])
        self.assertEqual(str(version_instance), "1.2.3")


    def test_version_constructor_no_values(self):
        """
        Tests for Version constructor no values.
        """

        version_instance = dogtail.version.Version()
        self.assertEqual(str(version_instance), "")


    def test_version_constructor_both_values_respect_snake_case(self):
        """
        Tests for Version constructor both values given, respect snake case value.
        """

        version_instance = dogtail.version.Version(version_list=[1, 2, 3], versionList=[4, 5, 6])
        self.assertEqual(str(version_instance), "1.2.3")
        self.assertNotEqual(str(version_instance), "4.5.6")
