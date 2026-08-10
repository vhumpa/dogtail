#!/usr/bin/python3
"""
Handling for Accessible TableCell.
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


@logging_class.log_a_class
class AccessibleTableCell:
    """
    TableCell class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_column_header_cells(acc_object):
        """
        Returns the column headers as an array of cell accessibles.
        """

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_column_header_cells()

        return Atspi.TableCell.get_column_header_cells(acc_object)


    @staticmethod
    def get_column_index(acc_object):
        """
        Returns the column index.
        """

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_column_index()

        return Atspi.TableCell.get_column_index(acc_object)


    @staticmethod
    def get_column_span(acc_object):
        """
        Returns the number of columns occupied by this cell accessible. The returned
        values are meaningful only if the table cell has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_column_span()

        return Atspi.TableCell.get_column_span(acc_object)


    @staticmethod
    def get_position(acc_object):
        """
        Retrieves the tabular position of this cell.
        """

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_position()

        return Atspi.TableCell.get_position(acc_object)


    @staticmethod
    def get_row_column_span(acc_object):
        """
        Gets the row and column indexes and extents of this cell accessible.
        The returned values are meaningful only if the table cell has both STATE_VISIBLE
        and STATE_SHOWING.
        """

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_row_column_span()

        return Atspi.TableCell.get_row_column_span(acc_object)


    @staticmethod
    def get_row_header_cells(acc_object):
        """
        Returns the row headers as an array of cell accessibles.
        """

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_row_header_cells()

        return Atspi.TableCell.get_row_header_cells(acc_object)


    @staticmethod
    def get_row_span(acc_object):
        """
        Returns the number of rows occupied by this cell accessible. The returned values
        are meaningful only if the table cell has both STATE_VISIBLE and STATE_SHOWING.
        """

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_row_span()

        return Atspi.TableCell.get_row_span(acc_object)


    @staticmethod
    def get_table(acc_object):
        """
        Returns a reference to the accessible of the containing table.
        """

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_table()

        return Atspi.TableCell.get_table(acc_object)
