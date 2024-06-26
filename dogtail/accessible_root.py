#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=import-error

from accessible_utilities import AccessibleUtilities

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

        return [x.get_name() for x in AccessibleUtilities.get_all_applications()]


    @staticmethod
    def application(application_name):
        """
        Gets an application by name, returning an Application instance or raising an
        exception.
        """

        return AccessibleUtilities.get_application_named(application_name)
