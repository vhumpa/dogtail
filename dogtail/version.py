# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from packaging import version
from dogtail.logging import debug_log

"""
Handles versioning of software packages
"""

__author__ = """
Dave Malcolm <dmalcolm@redhat.com>
"""

class Version:
    """
    Class representing a version of a software package.
    Stored internally as a list of subversions, from major to minor.
    Overloaded comparison operators ought to work sanely.
    """

    def __init__(self, versionList):
        debug_log("Version class constructor: '%s':'%s'" % \
            (type(versionList), str(versionList)))
        self.api_version = ".".join(str(x) for x in versionList) if isinstance(versionList, list) else versionList


    @classmethod
    def fromString(cls, versionString):
        debug_log("Getting version from Version.fromString deprecated, use constructor with string.")
        instance = Version(versionString)
        return instance


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
