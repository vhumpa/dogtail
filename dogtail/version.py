#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
Handles versioning of software packages.
"""

# pylint: disable=line-too-long
# ruff: noqa: E501

__author__ = "Dave Malcolm <dmalcolm@redhat.com>"

from packaging import version

from dogtail.logging import logging_class
LOGGING = logging_class.logger


class Version:
    """
    Class representing a version of a software package.
    Stored internally as a list of subversions, from major to minor.
    Overloaded comparison operators ought to work sanely.
    """

    def __init__(self, version_list = None, versionList = None): # pylint: disable=invalid-name
        LOGGING.debug(f"Version class constructor: '{type(versionList)}':'{str(versionList)}'")

        self.validate_version_to_use = None

        # Validate inputs, keeping the old variable.
        if version_list is None and versionList is None:
            LOGGING.debug("No version provided. Using empty string.")
            self.api_version = ""

        elif version_list and versionList:
            LOGGING.debug(f"Two versions provided. Using the '{str(version_list)}'.")
            self.validate_version_to_use = version_list

        elif version_list:
            self.validate_version_to_use = version_list

        elif versionList:
            self.validate_version_to_use = versionList

        # Validate type of input.
        if isinstance(self.validate_version_to_use, list):
            self.api_version = ".".join(str(x) for x in self.validate_version_to_use)

        elif isinstance(self.validate_version_to_use, str):
            self.api_version = self.validate_version_to_use


    @classmethod
    def from_string(cls, version_string):
        """
        Get Version Instance from string.

        :param version_string: String representation of version.
        :type version_string: str

        :return: Instance of Version.
        :rtype: Version
        """

        LOGGING.debug("Getting version from Version.from_string deprecated, use constructor with string.")
        instance = Version(version_string)
        return instance


    @classmethod
    def fromString(cls, versionString): # pylint: disable=invalid-name
        """
        Get Version Instance from string. Wrapper around from_string for compatibility.
        """
        return Version.from_string(version_string=versionString)


    def __str__(self):
        return self.api_version


    def __lt__(self, other):
        return version.parse(self.api_version) < version.parse(other.api_version)


    def __le__(self, other):
        return version.parse(self.api_version) <= version.parse(other.api_version)


    def __eq__(self, other):
        return version.parse(self.api_version) == version.parse(other.api_version)


    def __ne__(self, other):
        return version.parse(self.api_version) != version.parse(other.api_version)


    def __gt__(self, other):
        return version.parse(self.api_version) > version.parse(other.api_version)


    def __ge__(self, other):
        return version.parse(self.api_version) >= version.parse(other.api_version)
