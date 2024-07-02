#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# ruff: noqa: E402
# ruff: noqa: E501

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

# TODO To be change to dogtail.logging before release.
from dogtail._logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessible_object import AccessibleObject

class AccessibleState:
    """
    State class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_active(acc_object):
        """
        Get active state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.ACTIVE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.ACTIVE)


    @staticmethod
    def get_focusable(acc_object):
        """
        Get focusable state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.FOCUSABLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.FOCUSABLE)



    @staticmethod
    def get_focused(acc_object):
        """
        Get focused state.
        """
        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.FOCUSED)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.FOCUSED)



    @staticmethod
    def get_pressed(acc_object):
        """
        Get pressed state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.PRESSED)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.PRESSED)


    @staticmethod
    def get_resizable(acc_object):
        """
        Get resizable state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.RESIZABLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.RESIZABLE)


    @staticmethod
    def get_sensitive(acc_object):
        """
        Get sensitive state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.SENSITIVE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.SENSITIVE)


    @staticmethod
    def get_showing(acc_object):
        """
        Get showing state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.SHOWING)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.SHOWING)


    @staticmethod
    def get_visible(acc_object):
        """
        Get visible state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.VISIBLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.VISIBLE)


    @staticmethod
    def get_checked(acc_object):
        """
        Get checked state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.CHECKED)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.CHECKED)


    @staticmethod
    def get_checkable(acc_object):
        """
        Get checkable state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.CHECKABLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.CHECKABLE)


    @staticmethod
    def get_read_only(acc_object):
        """
        Get read_only state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.READ_ONLY)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.READ_ONLY)


    @staticmethod
    def get_collapsed(acc_object):
        """
        Get collapsed state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.COLLAPSED)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.COLLAPSED)


    @staticmethod
    def get_editable(acc_object):
        """
        Get editable state.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.EDITABLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.EDITABLE)


    @staticmethod
    def get_accessible_states(acc_object):
        """
        Get states as Accessible objects.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.EDITABLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.StateSet.get_states(Atspi.Accessible.get_state_set(acc_object))


    @staticmethod
    def get_string_states(acc_object):
        """
        Get states as strings.
        """

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.EDITABLE)
            return False # TODO, figure out how Newton defines it.

        return "TODO" # TODO, translate state types on object to strings.
