#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=import-error
# ruff: noqa: E402

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

# TODO To be change to dogtail.logging before release.
from _logging import logging_class
LOGGING = logging_class.logger


from accessible_object import AccessibleObject


class AccessibleSelection:
    """
    Selection class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def select_all(acc_object):
        """
        Selects all children.
        """

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            acc_object.select_all()
        else:
            Atspi.Selection.select_all(acc_object)


    @staticmethod
    def deselect_all(acc_object):
        """
        Deselects all children.
        """

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        if AccessibleObject.is_newton(acc_object):
            acc_object.clear_selection()
        else:
            Atspi.Selection.clear_selection(acc_object)


    @staticmethod
    def select(acc_object):
        """
        Selects a child.
        """

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        parent = AccessibleObject.get_parent_checked(acc_object)

        if AccessibleObject.is_newton(acc_object):
            acc_object.select_child(parent, acc_object.get_index_in_parent())
        else:
            Atspi.Selection.select_child(parent, acc_object.get_index_in_parent())


    @staticmethod
    def deselect(acc_object):
        """
        Deselects a child.
        """

        if not AccessibleObject.is_selection(acc_object):
            LOGGING.debug("This object does not have Atspi.Selection interface.")

        parent = AccessibleObject.get_parent_checked(acc_object)

        if AccessibleObject.is_newton(acc_object):
            acc_object.deselect_child(parent, acc_object.get_index_in_parent())
        else:
            Atspi.Selection.deselect_child(parent, acc_object.get_index_in_parent())
