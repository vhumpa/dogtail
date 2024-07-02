#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=import-error
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# ruff: noqa: E402


# TODO To be change to dogtail.logging before release.
from dogtail._logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessible_utilities import AccessibleUtilities

class AccessibleRoot:
    """
    Root class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def applications():
        """
        Get all applications.
        """

        return AccessibleUtilities.get_all_applications()


    @staticmethod
    def application(application_name):
        """
        Gets an application by name, returning an Application instance or raising an
        exception.
        """

        return AccessibleUtilities.get_application_named(application_name)
