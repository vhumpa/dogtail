# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from packaging import version
from dogtail.logging import debug_message

"""
Handles versioning of software packages
"""

__author__ = "Dave Malcolm <dmalcolm@redhat.com>"

class Version:
    """
    Class representing a version of a software package.
    Stored internally as a list of subversions, from major to minor.
    Overloaded comparison operators ought to work sanely.
    """

    def __init__(self, versionList):
        debug_message(message="Version class init.")
        self.api_version = '.'.join(versionList) if isinstance(versionList, list) else versionList


    def fromString(self, versionString):
        debug_message(message="Getting version from string.")
        self.api_version = versionString


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
