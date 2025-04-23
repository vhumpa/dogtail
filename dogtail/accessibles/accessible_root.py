#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=import-error
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=no-name-in-module
# ruff: noqa: E402


from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessibles.accessible_utilities import AccessibleUtilities


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

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleUtilities.get_all_applications()


    @staticmethod
    def application(application_name, **kwargs):
        """
        Gets an application by name, returning an Application instance or raising an
        exception.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        validated_retry = True
        validated_application_name = application_name
        # === Backward compatibility for 'appName' usage ===
        for key, val in kwargs.items():
            if "appName" in str(key):
                validated_application_name = val
            if "retry" in str(key):
                validated_retry = val
        # ===================================================

        return AccessibleUtilities.get_application_named(
            application_name=validated_application_name,
            retry=validated_retry
        )
