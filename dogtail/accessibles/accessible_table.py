#!/usr/bin/python3
"""
Class for Atspi.Table.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
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


class AccessibleTable:
    """
    Table class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def add_column_selection(acc_object, column):
        """
        Selects the specified column, adding it to the current column selection. Not
        all tables support column selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.add_column_selection(column)

        return Atspi.Table.add_column_selection(acc_object, column)


    @staticmethod
    def add_row_selection(acc_object, row):
        """
        Selects the specified row, adding it to the current row selection. Not all
        tables support row selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.add_row_selection(row)

        return Atspi.Table.add_row_selection(acc_object, row)


    @staticmethod
    def get_accessible_at(acc_object, row, column):
        """
        Gets the table cell at the specified row and column indices. To get the
        accessible object at a particular (x, y) screen coordinate, use
        Atspi.Component.get_accessible_at_point.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_accessible_at(row, column)

        return Atspi.Table.get_accessible_at(acc_object, row, column)


    @staticmethod
    def get_caption(acc_object):
        """
        Gets an accessible representation of the caption for an Atspi.Table.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_caption()

        return Atspi.Table.get_caption(acc_object)


    @staticmethod
    def get_column_at_index(acc_object, index):
        """
        Gets the table column index occupied by the child at a particular 1-D child
        index. See Atspi.Table.get_index_at, Atspi.Table.get_row_at_index.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_column_at_index(index)

        return Atspi.Table.get_column_at_index(acc_object, index)


    @staticmethod
    def get_column_description(acc_object, column):
        """
        Gets a text description of a particular table column. This differs from
        Atspi.Table.get_column_header, which returns an #Accessible.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_column_description(column)

        return Atspi.Table.get_column_description(acc_object, column)


    @staticmethod
    def get_column_extent_at(acc_object, row, column):
        """
        Gets the number of columns spanned by the table cell at the specific row and
        column (some tables can have cells which span multiple rows and/or columns).
        The returned values are meaningful only if the Table has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_column_extent_at(row, column)

        return Atspi.Table.get_column_extent_at(acc_object, row, column)


    @staticmethod
    def get_column_header(acc_object, column):
        """
        Gets the header associated with a table column, if available. This differs from
        Atspi.Table.get_column_description, which returns a string.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_column_header(column)

        return Atspi.Table.get_column_header(acc_object, column)


    @staticmethod
    def get_index_at(acc_object, row, column):
        """
        Gets the 1-D child index corresponding to the specified 2-D row and column
        indices. To get the accessible object at a particular (x, y) screen coordinate,
        use Atspi.Component.get_accessible_at_point. See Atspi.Table.get_row_at_index,
        Atspi.Table.get_column_at_index
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_index_at(row, column)

        return Atspi.Table.get_index_at(acc_object, row, column)


    @staticmethod
    def get_n_columns(acc_object):
        """
        Gets the number of columns in an Atspi.Table, exclusive of any columns that are
        programmatically hidden, but inclusive of columns that may be outside of the
        current scrolling window or viewport.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_n_columns()

        return Atspi.Table.get_n_columns(acc_object)


    @staticmethod
    def get_n_rows(acc_object):
        """
        Gets the number of rows in an Atspi.Table, exclusive of any rows that are
        programmatically hidden, but inclusive of rows that may be outside of the
        current scrolling window or viewport.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_n_rows()

        return Atspi.Table.get_n_rows(acc_object)


    @staticmethod
    def get_n_selected_columns(acc_object):
        """
        Queries a table to find out how many columns are currently selected. Not all
        tables support column selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_n_selected_columns()

        return Atspi.Table.get_n_selected_columns(acc_object)


    @staticmethod
    def get_n_selected_rows(acc_object):
        """
        Query a table to find out how many rows are currently selected. Not all tables
        support row selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_n_selected_rows()

        return Atspi.Table.get_n_selected_rows(acc_object)


    @staticmethod
    def get_row_at_index(acc_object, index):
        """
        Gets the table row index occupied by the child at a particular 1-D child index.
        See Atspi.Table.get_index_at, Atspi.Table.get_column_at_index.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_row_at_index(index)

        return Atspi.Table.get_row_at_index(acc_object, index)


    @staticmethod
    def get_row_column_extents_at_index(acc_object, index):
        """
        Given a child index, determines the row and column indices and extents, and
        whether the cell is currently selected. If the child at index is not a cell
        (for instance, if it is a summary, caption, etc.), False is returned.
        The returned values are meaningful only if the Table has both STATE_VISIBLE and
        STATE_SHOWING.

        Return type:

        (bool, row: int, col: int, row_extents: int, col_extents: int, is_selected: bool)

        Example: If the Atspi.Table child at index '6' extends across columns 5 and 6 of
        row 2 of an Atspi.Table instance, and is currently selected, then

        retval = Atspi.Table.get_row_column_extents_at_index
        (table, 6, row, col, row_extents, col_extents, is_selected);

        will return True, and after the call row, col, row_extents, col_extents, and
        is_selected will contain 2, 5, 1, 2, and True, respectively.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_row_column_extents_at_index(index)

        return Atspi.Table.get_row_column_extents_at_index(acc_object, index)


    @staticmethod
    def get_row_description(acc_object, row):
        """
        Gets a text description of a particular table row. This differs from
        Atspi.Table.get_row_header, which returns an Atspi.Accessible.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_row_description(row)

        return Atspi.Table.get_row_description(acc_object, row)


    @staticmethod
    def get_row_extent_at(acc_object, row, column):
        """
        Gets the number of rows spanned by the table cell at the specific row and
        column. (some tables can have cells which span multiple rows and/or columns).
        The returned values are meaningful only if the Table has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_row_extent_at(row, column)

        return Atspi.Table.get_row_extent_at(acc_object, row, column)


    @staticmethod
    def get_row_header(acc_object, row):
        """
        Gets the header associated with a table row, if available. This differs from
        Atspi.Table.get_row_description, which returns a string.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_row_header(row)

        return Atspi.Table.get_row_header(acc_object, row)


    @staticmethod
    def get_selected_columns(acc_object):
        """
        Queries a table for a list of indices of columns which are currently selected.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_selected_columns()

        return Atspi.Table.get_selected_columns(acc_object)


    @staticmethod
    def get_selected_rows(acc_object):
        """
        Queries a table for a list of indices of rows which are currently selected.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_selected_rows()

        return Atspi.Table.get_selected_rows(acc_object)


    @staticmethod
    def get_summary(acc_object):
        """
        Gets an accessible object which summarizes the contents of an Atspi.Table.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_summary()

        return Atspi.Table.get_summary(acc_object)


    @staticmethod
    def is_column_selected(acc_object, column):
        """
        Determines whether specified table column is selected. Not all tables support
        column selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.is_column_selected(column)

        return Atspi.Table.is_column_selected(acc_object, column)


    @staticmethod
    def is_row_selected(acc_object, row):
        """
        Determines whether a table row is selected. Not all tables support row
        selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.is_row_selected(row)

        return Atspi.Table.is_row_selected(acc_object, row)


    @staticmethod
    def is_selected(acc_object, row, column):
        """
        Determines whether the cell at a specific row and column is selected.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.is_selected(row, column)

        return Atspi.Table.is_selected(acc_object, row, column)


    @staticmethod
    def remove_column_selection(acc_object, column):
        """
        De-selects the specified column, removing it from the current column selection.
        Not all tables support column selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.remove_column_selection(column)

        return Atspi.Table.remove_column_selection(acc_object, column)


    @staticmethod
    def remove_row_selection(acc_object, row):
        """
        De-selects the specified row, removing it from the current row selection. Not
        all tables support row selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_table(acc_object):
            LOGGING.debug("This object does not have Atspi.Table interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.remove_row_selection(row)

        return Atspi.Table.remove_row_selection(acc_object, row)
