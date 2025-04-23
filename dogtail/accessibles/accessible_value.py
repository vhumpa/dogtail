#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# ruff: noqa: E402

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessibles.accessible_object import AccessibleObject


class AccessibleValue:
    """
    Value class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_current_value(acc_object):
        """
        Gets the current value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if not AccessibleObject.is_value(acc_object):
            LOGGING.debug("Accessible object does not have a Value interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_current_value()

        return Atspi.Value.get_current_value(acc_object)


    @staticmethod
    def get_maximum_value(acc_object):
        """
        Gets the maximum allowed value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if not AccessibleObject.is_value(acc_object):
            LOGGING.debug("Accessible object does not have a Value interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_maximum_value()

        return Atspi.Value.get_maximum_value(acc_object)


    @staticmethod
    def get_minimum_increment(acc_object):
        """
        Gets the minimum increment by which an Atspi.Value can be adjusted.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if not AccessibleObject.is_value(acc_object):
            LOGGING.debug("Accessible object does not have a Value interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_minimum_increment()

        return Atspi.Value.get_minimum_increment(acc_object)


    @staticmethod
    def get_minimum_value(acc_object):
        """
        Gets the minimum allowed value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if not AccessibleObject.is_value(acc_object):
            LOGGING.debug("Accessible object does not have a Value interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_minimum_value()

        return Atspi.Value.get_minimum_value(acc_object)


    @staticmethod
    def set_current_value(acc_object, set_value):
        """
        Set a value to an Accessible Value object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if not AccessibleObject.is_value(acc_object):
            LOGGING.debug("Accessible object does not have a Value interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.set_current_value(set_value)

        return Atspi.Value.set_current_value(acc_object, set_value)
