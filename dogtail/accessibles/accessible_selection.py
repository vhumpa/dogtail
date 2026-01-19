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


class AccessibleSelection:
    """
    Selection class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def clear_selection(acc_object):
        """
        Clears the current selection, removing all selected children from the specified
        Atspi.Selection implementor's selection list.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.clear_selection()

        return Atspi.Selection.clear_selection(acc_object)


    @staticmethod
    def deselect_child(acc_object, child_index):
        """
        Deselects a specific child of an Atspi.Selection. Note that child_index is the
        index of the child in the parent container.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.deselect_child(child_index)

        return Atspi.Selection.deselect_child(acc_object, child_index)


    @staticmethod
    def deselect_selected_child(acc_object, selected_child_index):
        """
        Removes a child from the selected children list of an Atspi.Selection. Note that
        selected_child_index is the index in the selected-children list, not the index
        in the parent container. selected_child_index in this method, and child_index in
        Atspi.Selection.select_child are asymmetric.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.deselect_selected_child(selected_child_index)

        return Atspi.Selection.deselect_selected_child(acc_object, selected_child_index)


    @staticmethod
    def get_n_selected_children(acc_object):
        """
        Gets the number of children of an Atspi.Selection implementor which are
        currently selected.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_n_selected_children()

        return Atspi.Selection.get_n_selected_children(acc_object)


    @staticmethod
    def get_selected_child(acc_object, selected_child_index):
        """
        Gets the i-th selected Atspi.Accessible child of an Atspi.Selection. Note that
        selected_child_index refers to the index in the list of 'selected' children and
        generally differs from that used in Atspi.Accessible.get_child_at_index or
        returned by Atspi.Accessible.get_index_in_parent. selected_child_index must lie
        between 0 and Atspi.Selection.get_n_selected_children - 1, inclusive.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_selected_child(selected_child_index)

        return Atspi.Selection.get_selected_child(acc_object, selected_child_index)


    @staticmethod
    def is_child_selected(acc_object, child_index):
        """
        Determines whether a particular child of an Atspi.Selection implementor is
        currently selected. Note that child_index is the index into the standard
        Atspi.Accessible container's list of children.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.is_child_selected(child_index)

        return Atspi.Selection.is_child_selected(acc_object, child_index)


    @staticmethod
    def select_all(acc_object):
        """
        Attempts to select all of the children of an Atspi.Selection implementor. Not
        all Atspi.Selection implementors support this operation.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.select_all()

        return Atspi.Selection.select_all(acc_object)


    @staticmethod
    def select_child(acc_object, child_index):
        """
        Adds a child to the selected children list of an Atspi.Selection. For
        Atspi.Selection implementors that only allow single selections, this may replace
        the (single) current selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.select_child(child_index)

        return Atspi.Selection.select_child(acc_object, child_index)


    @staticmethod
    def select(acc_object):
        """
        Selects a child.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        parent = AccessibleObject.get_parent_checked(acc_object)

        if AccessibleObject.is_newton(acc_object):
            return acc_object.select_child(parent, acc_object.get_index_in_parent())

        return Atspi.Selection.select_child(parent, acc_object.get_index_in_parent())


    @staticmethod
    def deselect(acc_object):
        """
        Deselects a child.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        parent = AccessibleObject.get_parent_checked(acc_object)

        if AccessibleObject.is_newton(acc_object):
            return acc_object.deselect_child(parent, acc_object.get_index_in_parent())

        return Atspi.Selection.deselect_child(parent, acc_object.get_index_in_parent())
