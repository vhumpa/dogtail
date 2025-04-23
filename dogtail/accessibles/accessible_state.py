#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# ruff: noqa: E402
# ruff: noqa: E501

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessibles.accessible_object import AccessibleObject


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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.RESIZABLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.RESIZABLE)


    @staticmethod
    def get_selected(acc_object):
        """
        Get selected state.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.SELECTED)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.SELECTED)


    @staticmethod
    def get_selectable(acc_object):
        """
        Get selectable state.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.SELECTABLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.SELECTABLE)


    @staticmethod
    def get_sensitive(acc_object):
        """
        Get sensitive state.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.EDITABLE)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.EDITABLE)


    @staticmethod
    def get_armed(acc_object):
        """
        Get armed state.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.ARMED)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.ARMED)


    @staticmethod
    def get_invalid(acc_object):
        """
        Get invalid state.
        """

        #LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.INVALID)
            return False # TODO, figure out how Newton defines it.

        return Atspi.Accessible.get_state_set(acc_object).contains(Atspi.StateType.INVALID)


    @staticmethod
    def get_accessible_states(acc_object):
        """
        Get states as Accessible objects.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            # return acc_object.get_state_set(acc_object).contains(Newton.StateType.EDITABLE)
            return False # TODO, figure out how Newton defines it.

        return "TODO" # TODO, translate state types on object to strings.
