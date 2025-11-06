#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=no-name-in-module
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# ruff: noqa: E402
# ruff: noqa: E501

import os

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import warnings

warnings.filterwarnings("ignore", "g_object_unref")

from .logging import logging_class
LOGGING = logging_class.logger


from .accessibles.accessible_actions import AccessibleActions
from .accessibles.accessible_component import AccessibleComponent
from .accessibles.accessible_editable_text import AccessibleEditableText
from .accessibles.accessible_hypertext import AccessibleHypertext
from .accessibles.accessible_image import AccessibleImage
from .accessibles.accessible_object import AccessibleObject, SearchError
from .accessibles.accessible_root import AccessibleRoot
from .accessibles.accessible_selection import AccessibleSelection
from .accessibles.accessible_state import AccessibleState
from .accessibles.accessible_table import AccessibleTable
from .accessibles.accessible_table_cell import AccessibleTableCell
from .accessibles.accessible_text import AccessibleText
from .accessibles.accessible_utilities import AccessibleUtilities
from .accessibles.accessible_value import AccessibleValue

from dogtail.predicate import (
    GenericPredicate,
    IsAMenuNamed,
    IsAMenuItemNamed,
    IsATextEntryNamed,
    IsAButtonNamed,
    IsLabelledAs,
    IsNamed,
    IsATabNamed,
    IsAWindowNamed,
    IsADialogNamed,
)

from dogtail.ponytail_helper import ponytail_helper
from dogtail.rawinput import click, point, double_click
from dogtail.utils import do_delay


class Node(object):
    """
    Main dogtail API definition.
    """

    LOGGING.debug("Initiating dogtail api.")

    event_listeners = {}

    # Keep session as a variable.
    session_type = "x11"
    if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
        session_type = "wayland"


    # I understand this a little better now.
    def register_event_listener(self, client, *names):
        """
        Register an event listener.
        In the future we might need to register all event listeners to get updates.
        """

        try:
            listener = self.event_listeners[client]
        except Exception:
            self.event_listeners[client] = Atspi.EventListener.new(self.dummy_callback)
            listener = self.event_listeners[client]

        for name in names:
            # If Newton do X.
                # Newton.event_listener.register...
            # else: Do Atspi
            Atspi.EventListener.register(listener, name)


    # I understand this a little better now.
    def deregister_event_listener(self, client, *names):
        """
        Register an event listener.
        """

        try:
            listener = self.event_listeners[client]
        except Exception:
            return

        for name in names:
            # If Newton do X.
                # Newton.event_listener.deregister...
            # else: Do Atspi
            Atspi.EventListener.deregister(listener, name)


    # I understand this a little better now.
    def dummy_callback(self, event):
        """
        Define what to do when a registered event is fired.
        In this case it will print what event was fired and what source was the cause.
        """

        LOGGING.debug("Dummy callback.")

        # The Atspi object.
        source = event.source

        if isinstance(source, Atspi.Accessible):
            try:
                name = Atspi.Accessible.get_name(source)
                role_name = Atspi.Accessible.get_role_name(source)
                source_description = f"source: [ {role_name} | {name} ]"
            except Exception as e:
                source_description = f"[DEAD] - '{e}'"
        else:
            source_description = ""

        # Not printing any unnamed objects, which will flood the log.
        if "| ]" not in source_description:
            print(f"Event: '{event.type}' '{source_description}'")


    def do_action(self, index):
        """
        Invoke the action indicated by index on the object implementing Atspi.Action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.do_action(self, index)


    def get_action_description(self, index):
        """
        Get the description of the index-th Action on the object implementing Atspi.Action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.get_action_description(self, index)


    def get_action_name(self, index):
        """
        Get the name of the index-th Action on the object implementing Atspi.Action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.get_action_description(self, index)


    def get_key_binding(self, index):
        """
        Get the keybindings of the index-th Action on the object implementing Atspi.Action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.get_key_binding(self, index)


    def get_localized_name(self, index):
        """
        Get the localized name of the index-th Action on the object implementing Atspi.Action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.get_localized_name(self, index)


    @property
    def actions(self):
        """
        Get dictionary of actions.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.get_actions(self)


    def do_action_named(self, named_action):
        """
        Invoke the action indicated by its name on the object implementing Atspi.Action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.do_action_named(self, named_action)


    def contains(self, x_coordinate, y_coordinate, coordinate_type=None):
        """
        Queries whether a given Atspi.Component contains a particular point.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.contains(self, x_coordinate, y_coordinate, coordinate_type)


    def get_accessible_at_point(self, x_coordinate, y_coordinate, coordinate_type=None):
        """
        Gets the accessible child at a given coordinate within an Atspi.Component.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_accessible_at_point(self, x_coordinate, y_coordinate, coordinate_type)


    def get_alpha(self):
        """
        Gets the opacity/alpha value of a component, if alpha blending is in use.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_alpha(self)


    def get_extents(self):
        """
        Gets the bounding box of the specified Atspi.Component. The returned values are
        meaningful only if the Component has both STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_extents(self)


    @property
    def extents(self):
        """
        Gets the bounding box of the specified Atspi.Component. The returned values are
        meaningful only if the Component has both STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.get_extents()


    def get_layer(self):
        """
        Queries which layer the component is painted into, to help determine its
        visibility in terms of stacking order.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_layer(self)


    def get_mdi_z_order(self):
        """
        Queries the z stacking order of a component which is in the MDI or window layer.
        (Bigger z-order numbers mean nearer the top)
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_mdi_z_order(self)


    def get_position(self):
        """
        A tuple containing the position of the Accessible: (x, y).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_position(self)


    @property
    def position(self):
        """
        A tuple containing the position of the Accessible: (x, y).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.get_position()


    def get_size(self):
        """
        A tuple containing the size of the Accessible: (w, h)
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_size(self)


    @property
    def size(self):
        """
        A tuple containing the size of the Accessible: (w, h).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.get_size()


    def grab_focus(self):
        """
        Grab focus.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.grab_focus(self)


    def scroll_to(self, scroll_type):
        """
        Scrolls whatever container of the Atspi.Component object so it becomes visible
        on the screen.

        Atspi.ScrollType.TOP_LEFT = 0
        Atspi.ScrollType.BOTTOM_RIGHT  = 1
        Atspi.ScrollType.TOP_EDGE  = 2
        Atspi.ScrollType.BOTTOM_EDGE  = 3
        Atspi.ScrollType.LEFT_EDGE  = 4
        Atspi.ScrollType.RIGHT_EDGE  = 5
        Atspi.ScrollType.ANYWHERE  = 6
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.scroll_to(self, scroll_type)


    def scroll_to_point(self, coordinate_type, x_coordinate, y_coordinate):
        """
        Scrolls whatever container of the Atspi.Component object so it becomes visible
        on the screen.

        Atspi.CoordType.SCREEN = 0
        Atspi.CoordType.WINDOW = 1
        Atspi.CoordType.PARENT = 2
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.scroll_to_point(
            self,
            coordinate_type,
            x_coordinate,
            y_coordinate
        )


    def set_extents(self, x_coordinate, y_coordinate, width, height, coordinate_type):
        """
        Moves and resizes the specified component.

        Atspi.CoordType.SCREEN = 0
        Atspi.CoordType.WINDOW = 1
        Atspi.CoordType.PARENT = 2
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.set_extents(
            self,
            x_coordinate,
            y_coordinate,
            width,
            height,
            coordinate_type
        )


    def set_position(self, x_coordinate, y_coordinate, coordinate_type):
        """
        Moves the component to the specified position.

        Atspi.CoordType.SCREEN = 0
        Atspi.CoordType.WINDOW = 1
        Atspi.CoordType.PARENT = 2
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.set_position(
            self,
            x_coordinate,
            y_coordinate,
            coordinate_type
        )


    def set_size(self,width, height):
        """
        Resizes the specified component to the given pixel dimensions.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.set_size(self, width, height)


    def get_center(self):
        """
        A tuple containing the center of the Accessible: (x, y).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_center(self)


    @property
    def center(self):
        """
        A tuple containing the center of the Accessible: (x, y).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.get_center()


    def copy_text(self, start_position=None, end_position=None):
        """
        Copies text from an Atspi.EditableText object into the system clipboard.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleEditableText.copy_text(self, start_position, end_position)


    def cut_text(self, start_position=None, end_position=None):
        """
        Deletes text from an Atspi.EditableText object, copying the excised portion into
        the system clipboard.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleEditableText.cut_text(self, start_position, end_position)


    def delete_text(self, start_position=None, end_position=None):
        """
        Deletes text from an Atspi.EditableText object, without copying the excised
        portion into the system clipboard.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleEditableText.delete_text(self, start_position, end_position)


    def insert_text(self, text, position=0, length=0):
        """
        Inserts text into an Atspi.EditableText object. As with all character offsets,
        the specified position may not be the same as the resulting byte offset, since
        the text is in a variable-width encoding.

        Deliberately moving parameters around so that the text is first.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleEditableText.insert_text(self, text, position, length)


    def paste_text(self, position):
        """
        Inserts text from the system clipboard into an Atspi.EditableText object. As
        with all character offsets, the specified position may not be the same as the
        resulting byte offset, since the text is in a variable-width encoding.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleEditableText.paste_text(self, position)


    def set_text_contents(self, new_contents):
        """
        Replace the entire text contents of an Atspi.EditableText object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleEditableText.set_text_contents(self, new_contents)


    def get_link(self, link_index):
        """
        Gets the Atspi.Hyperlink object at a specified index.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleHypertext.get_link(self, link_index)


    def get_link_index(self, character_offset):
        """
        Gets the index of the Atspi.Hyperlink object at a specified character offset.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleHypertext.get_link_index(self, character_offset)


    def get_n_links(self):
        """
        Gets the total number of Atspi.Hyperlink objects that an Atspi.Hypertext
        implementor has.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleHypertext.get_n_links(self)


    def get_image_description(self):
        """
        Gets the description of the image displayed in an Atspi.Image object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleImage.get_image_description(self)


    def get_image_extents(self, coordinate_type=None):
        """
        Gets the bounding box of the image displayed in a specified Atspi.Image
        implementor. The returned values are meaningful only if the Image has both
        STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleImage.get_image_extents(self, coordinate_type)


    def get_image_locale(self):
        """
        Gets the locale associated with an image and its textual representation.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleImage.get_image_locale(self)


    def get_image_position(self, coordinate_type=None):
        """
        Gets the minimum x and y coordinates of the image displayed in a specified
        Atspi.Image implementor. The returned values are meaningful only if the Image
        has both STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleImage.get_image_position(self, coordinate_type)


    def get_image_size(self):
        """
        Gets the size of the image displayed in a specified Atspi.Image object.
        The returned values are meaningful only if the Image has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleImage.get_image_size(self)


    def clear_selection(self):
        """
        Clears the current selection, removing all selected children from the specified
        Atspi.Selection implementor's selection list.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.clear_selection(self)


    def deselect_all(self):
        """
        Deselects all children.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.clear_selection()


    def deselect_child(self, child_index):
        """
        Deselects a specific child of an Atspi.Selection. Note that child_index is the
        index of the child in the parent container.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.deselect_child(self, child_index)


    def deselect_selected_child(self, child_index):
        """
        Removes a child from the selected children list of an Atspi.Selection. Note that
        selected_child_index is the index in the selected-children list, not the index
        in the parent container. selected_child_index in this method, and child_index in
        Atspi.Selection.select_child are asymmetric.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.deselect_selected_child(self, child_index)


    def get_n_selected_children(self):
        """
        Gets the number of children of an Atspi.Selection implementor which are
        currently selected.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.get_n_selected_children(self)


    def get_selected_child(self, selected_child_index):
        """
        Gets the i-th selected Atspi.Accessible child of an Atspi.Selection. Note that
        selected_child_index refers to the index in the list of 'selected' children and
        generally differs from that used in Atspi.Accessible.get_child_at_index or
        returned by Atspi.Accessible.get_index_in_parent. selected_child_index must lie
        between 0 and Atspi.Selection.get_n_selected_children - 1, inclusive.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.get_selected_child(self, selected_child_index)


    def is_child_selected(self, child_index):
        """
        Determines whether a particular child of an Atspi.Selection implementor is
        currently selected. Note that child_index is the index into the standard
        Atspi.Accessible container's list of children.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.is_child_selected(self, child_index)


    def select_all(self):
        """
        Attempts to select all of the children of an Atspi.Selection implementor. Not
        all Atspi.Selection implementors support this operation.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.select_all(self)


    def select_child(self, child_index):
        """
        Adds a child to the selected children list of an Atspi.Selection. For
        Atspi.Selection implementors that only allow single selections, this may replace
        the (single) current selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.select_child(self, child_index)


    def select(self):
        """
        Selects a child.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.select(self)


    def deselect(self):
        """
        Deselects a child.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.deselect(self)


    @property
    def active(self):
        """
        Indicates this object can accept keyboard focus, which means all events
        resulting from typing on the keyboard will normally be passed to it when it has
        focus.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_active(self)


    @property
    def focusable(self):
        """
        Indicates this object can accept keyboard focus, which means all events
        resulting from typing on the keyboard will normally be passed to it when it has
        focus.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_focusable(self)


    @property
    def focused(self):
        """
        Indicates this object currently has the keyboard focus.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_focused(self)


    @property
    def pressed(self):
        """
        Indicates this object is currently pressed.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_pressed(self)


    @property
    def resizable(self):
        """
        Indicates the size of this object's size is not fixed.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_resizable(self)


    @property
    def selected(self):
        """
        Indicates this object is selected..
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_selected(self)


    @property
    def selectable(self):
        """
        Indicates this object is selected..
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_selectable(self)


    @property
    def sensitive(self):
        """
        Indicates this object is sensitive, e.g. to user interaction.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_sensitive(self)


    @property
    def showing(self):
        """
        Indicates this object, the object's parent, the object's parent's parent, and
        so on, are all 'shown' to the end-user, i.e. subject to “exposure” if blocking
        or obscuring objects do not interpose between this object and the top of the
        window stack.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_showing(self)


    @property
    def visible(self):
        """
        Indicates this object is visible, e.g. has been explicitly marked for exposure
        to the user.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_visible(self)


    @property
    def checked(self):
        """
        Indicates this object is currently checked.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_checked(self)


    @property
    def checkable(self):
        """
        Indicates this object has the potential to be checked, such as a checkbox or
        toggle-able table cell.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_checkable(self)


    @property
    def read_only(self):
        """
        Indicates that an object which is ENABLED and SENSITIVE has a value which can be
        read, but not modified, by the user.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_read_only(self)


    @property
    def collapsed(self):
        """
        Indicates this object is collapsed.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_collapsed(self)


    @property
    def editable(self):
        """
        Indicates the user can change the contents of this object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_editable(self)


    @property
    def armed(self):
        """
        Indicates that the object is armed.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_armed(self)


    @property
    def invalid(self):
        """
        Indicates that the object is invalid.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_invalid(self)


    @property
    def state_set(self):
        """
        Get states.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_accessible_states(self)


    def add_column_selection(self, column):
        """
        Selects the specified column, adding it to the current column selection. Not
        all tables support column selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.add_column_selection(self, column)


    def add_row_selection(self, row):
        """
        Selects the specified row, adding it to the current row selection. Not all
        tables support row selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.add_row_selection(self, row)


    def get_accessible_at(self, row, column):
        """
        Gets the table cell at the specified row and column indices. To get the
        accessible object at a particular (x, y) screen coordinate, use
        Atspi.Component.get_accessible_at_point.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_accessible_at(self, row, column)


    def get_caption(self):
        """
        Gets an accessible representation of the caption for an Atspi.Table.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_caption(self)


    def get_column_at_index(self, index):
        """
        Gets the table column index occupied by the child at a particular 1-D child
        index. See Atspi.Table.get_index_at, Atspi.Table.get_row_at_index.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_column_at_index(self, index)


    def get_column_description(self, column):
        """
        Gets a text description of a particular table column. This differs from
        Atspi.Table.get_column_header, which returns an #Accessible.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_column_description(self, column)


    def get_column_extent_at(self, row, column):
        """
        Gets the number of columns spanned by the table cell at the specific row and
        column (some tables can have cells which span multiple rows and/or columns).
        The returned values are meaningful only if the Table has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_column_extent_at(self, row, column)


    def get_column_header(self, column):
        """
        Gets the header associated with a table column, if available. This differs from
        Atspi.Table.get_column_description, which returns a string.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_column_header(self, column)


    def get_index_at(self, row, column):
        """
        Gets the 1-D child index corresponding to the specified 2-D row and column
        indices. To get the accessible object at a particular (x, y) screen coordinate,
        use Atspi.Component.get_accessible_at_point. See Atspi.Table.get_row_at_index,
        Atspi.Table.get_column_at_index
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_index_at(self, row, column)


    def get_n_columns(self):
        """
        Gets the number of columns in an Atspi.Table, exclusive of any columns that are
        programmatically hidden, but inclusive of columns that may be outside of the
        current scrolling window or viewport.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_n_columns(self)


    def get_n_rows(self):
        """
        Gets the number of rows in an Atspi.Table, exclusive of any rows that are
        programmatically hidden, but inclusive of rows that may be outside of the
        current scrolling window or viewport.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_n_rows(self)


    def get_n_selected_columns(self):
        """
        Queries a table to find out how many columns are currently selected. Not all
        tables support column selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_n_selected_columns(self)


    def get_n_selected_rows(self):
        """
        Query a table to find out how many rows are currently selected. Not all tables
        support row selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_n_selected_rows(self)


    def get_row_at_index(self, index):
        """
        Gets the table row index occupied by the child at a particular 1-D child index.
        See Atspi.Table.get_index_at, Atspi.Table.get_column_at_index.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_row_at_index(self, index)


    def get_row_column_extents_at_index(self, index):
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

        return AccessibleTable.get_row_column_extents_at_index(self, index)


    def get_row_description(self, row):
        """
        Gets a text description of a particular table row. This differs from
        Atspi.Table.get_row_header, which returns an Atspi.Accessible.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_row_description(self, row)


    def get_row_extent_at(self, row, column):
        """
        Gets the number of rows spanned by the table cell at the specific row and
        column. (some tables can have cells which span multiple rows and/or columns).
        The returned values are meaningful only if the Table has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_row_extent_at(self, row, column)


    def get_row_header(self, row):
        """
        Gets the header associated with a table row, if available. This differs from
        Atspi.Table.get_row_description, which returns a string.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_row_header(self, row)


    def get_selected_columns(self):
        """
        Queries a table for a list of indices of columns which are currently selected.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_selected_columns(self)


    def get_selected_rows(self):
        """
        Queries a table for a list of indices of rows which are currently selected.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_selected_rows(self)


    def get_summary(self):
        """
        Gets an accessible object which summarizes the contents of an Atspi.Table.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.get_summary(self)


    def is_column_selected(self, column):
        """
        Determines whether specified table column is selected. Not all tables support
        column selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.is_column_selected(self, column)


    def is_row_selected(self, row):
        """
        Determines whether a table row is selected. Not all tables support row
        selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.is_row_selected(self, row)


    def is_selected(self, row, column):
        """
        Determines whether the cell at a specific row and column is selected.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.is_selected(self, row, column)


    def remove_column_selection(self, column):
        """
        De-selects the specified column, removing it from the current column selection.
        Not all tables support column selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.remove_column_selection(self, column)


    def remove_row_selection(self, row):
        """
        De-selects the specified row, removing it from the current row selection. Not
        all tables support row selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTable.remove_row_selection(self, row)


    def get_column_header_cells(self):
        """
        Returns the column headers as an array of cell accessibles.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTableCell.get_column_header_cells(self)


    def get_column_index(self):
        """
        Returns the column index.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTableCell.get_column_index(self)


    def get_column_span(self):
        """
        Returns the number of columns occupied by this cell accessible. The returned
        values are meaningful only if the table cell has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTableCell.get_column_span(self)


    def get_cell_position(self):
        """
        Retrieves the tabular position of this cell.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTableCell.get_position(self)


    def get_row_column_span(self):
        """
        Gets the row and column indexes and extents of this cell accessible.
        The returned values are meaningful only if the table cell has both STATE_VISIBLE
        and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTableCell.get_row_column_span(self)


    def get_row_header_cells(self):
        """
        Returns the row headers as an array of cell accessibles.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTableCell.get_row_header_cells(self)


    def get_row_span(self):
        """
        Returns the number of rows occupied by this cell accessible. The returned values
        are meaningful only if the table cell has both STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTableCell.get_row_span(self)


    def get_table(self):
        """
        Returns a reference to the accessible of the containing table.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleTableCell.get_table(self)


    def add_selection(self, start_offset, end_offset):
        """
        Selects some text (adds a text selection) in an Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.add_selection(self, start_offset, end_offset)


    def get_attribute_run(self, offset, include_defaults):
        """
        Gets a set of attributes applied to a range of text from an Atspi.Text object,
        optionally including its 'default' attributes.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_attribute_run(self, offset, include_defaults)


    def get_bounded_ranges(self, x, y, width, height, coord_type, clip_type_x, clip_type_y):
        """
        Gets the ranges of text from an Atspi.Text object which lie within the bounds
        defined by (x, y) and (x+'width', y+'height').
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_bounded_ranges(
            self,
            x,
            y,
            width,
            height,
            coord_type,
            clip_type_x,
            clip_type_y
        )


    def get_caret_offset(self):
        """
        Gets the current offset of the text caret in an Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_caret_offset(self)


    def get_character_at_offset(self, offset):
        """
        Gets the character at a given offset for an Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_character_at_offset(self, offset)


    def get_character_count(self):
        """
        Gets the character count of an #AccessibleText object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_character_count(self)


    def get_character_extents(self, offset, coord_type):
        """
        Gets a bounding box containing the glyph representing the character at a
        particular text offset. The returned values are meaningful only if the Text has
        both STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_character_extents(self, offset, coord_type)


    def get_default_attributes(self):
        """
        Gets the default attributes applied to an Atspi.Text object. The text attributes
        correspond to CSS attributes where possible. The combination of this attribute
        set and the attributes reported by Atspi.Text.get_text_attributes describes the
        entire set of text attributes over a range.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_default_attributes(self)


    def get_n_selections(self):
        """
        Gets the number of active non-contiguous selections for an Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_n_selections(self)


    def get_offset_at_point(self, x, y, coord_type):
        """
        Gets the character offset into the text at a given point.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_offset_at_point(self, x, y, coord_type)


    def get_range_extents(self, start_offset, end_offset, coord_type):
        """
        Gets the bounding box for text within a range in an Atspi.Text object.
        The returned values are meaningful only if the Text has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_range_extents(self, start_offset, end_offset, coord_type)


    def get_selection(self, selection_num):
        """
        Gets the bounds of the selection_num-th active text selection for an Atspi.Text
        object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_selection(self, selection_num)


    def get_string_at_offset(self, offset, granularity):
        """
        Gets a portion of the text exposed through an Atspi.Text according to a given
        offset and a specific granularity, along with the start and end offsets defining
        the boundaries of such a portion of text.

        New in version Atspi 2.9.90.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_string_at_offset(self, offset, granularity)


    def get_text(self, start_offset, end_offset):
        """
        Gets a range of text from an Atspi.Text object. The number of bytes in the
        returned string may exceed either end_offset or start_offset, since UTF-8 is a
        variable-width encoding.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_text(self, start_offset, end_offset)


    def get_text_after_offset(self, offset, coord_type):
        """
        Gets delimited text from an Atspi.Text object which follows a given text offset.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_text_after_offset(self, offset, coord_type)


    def get_text_at_offset(self, offset, coord_type):
        """
        Gets delimited text from an Atspi.Text object which includes a given text
        offset.

        Deprecated since version 2.10. Use Atspi.Text.get_string_at_offset.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_text_at_offset(self, offset, coord_type)


    def get_text_attribute_value(self, offset, attribute_name):
        """
        Gets the value of a named attribute at a given offset.

        Deprecated since version 2.10: Use Atspi.Text.get_text_attribute_value instead.

        Note: The deprecation note what to use seems wrong.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_text_attribute_value(self, offset, attribute_name)


    def get_text_attributes(self, offset):
        """
        Gets the attributes applied to a range of text from an Atspi.Text object.
        The text attributes correspond to CSS attributes where possible.

        Deprecated since version 2.10: Use Atspi.Text.get_text_attributes instead.

        Note: The deprecation note what to use seems wrong.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_text_attributes(self, offset)


    def get_text_before_offset(self, offset, coord_type):
        """
        Gets delimited text from an Atspi.Text object which precedes a given text
        offset.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_text_before_offset(self, offset, coord_type)


    def remove_selection(self, selection_num):
        """
        De-selects a text selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.remove_selection(self, selection_num)


    def scroll_substring_to(self, start_offset, end_offset, coord_type):
        """
        Scrolls whatever container of the Atspi.Text text range so it becomes visible
        on the screen.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.scroll_substring_to(self, start_offset, end_offset, coord_type)


    def scroll_substring_to_point(self, start_offset, end_offset, coord_type, x, y):
        """
        Scrolls whatever container of the Atspi.Text text range so it becomes visible
        on the screen at a given position.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.scroll_substring_to_point(
            self,
            start_offset,
            end_offset,
            coord_type,
            x,
            y
        )


    def set_caret_offset(self, new_offset):
        """
        Moves the text caret to a given position.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.set_caret_offset(self, new_offset)


    def set_selection(self, selection_num, start_offset, end_offset):
        """
        Changes the bounds of an existing Atspi.Text text selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.set_selection(self, selection_num, start_offset, end_offset)


    @property
    def text(self):
        """
        Define a 'text' property for Atspi object.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_all_text(self)


    @text.setter
    def text(self, content):
        """
        Define a 'text' setter for Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleEditableText.set_text_contents(self, content)


    def get_current_value(self):
        """
        Gets the current value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.get_current_value(self)


    @property
    def value(self):
        """
        Gets the current value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.get_current_value()


    @value.setter
    def value(self, new_value):
        """
        Gets the current value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.set_current_value(self, new_value)


    def get_maximum_value(self):
        """
        Gets the maximum allowed value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.get_maximum_value(self)


    @property
    def max_value(self):
        """
        Gets the maximum allowed value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.get_maximum_value()


    def get_minimum_increment(self):
        """
        Gets the minimum increment by which an Atspi.Value can be adjusted.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.get_minimum_increment(self)


    @property
    def min_value_increment(self):
        """
        Gets the minimum increment by which an Atspi.Value can be adjusted.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.get_minimum_increment()


    def get_minimum_value(self):
        """
        Gets the minimum allowed value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.get_minimum_value(self)


    @property
    def min_value(self):
        """
        Gets the minimum allowed value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.get_minimum_value()


    @property
    def toolkit(self):
        """
        Return string description of the toolkit we are using.
        """

        # TODO revisit, this will flood logs on position query.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleUtilities.get_toolkit(self)


    @property
    def window_id(self):
        """
        Return window_id of a node.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return ponytail_helper.get_window_id(self)


    @property
    def window_has_focus(self):
        """
        Check if window is focused.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if self.session_type != "wayland":
            LOGGING.info("Ponytail is not used in non Wayland session.")
            return False

        return ponytail_helper.get_window_has_focus()


    @property
    def id(self):
        """
        Define a 'id' property for Atspi object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_id(self)


    @property
    def name(self):
        """
        Define a 'name' property for Atspi object.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_name(self)


    @property
    def role(self):
        """
        Define a 'role property for Atspi object.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_role(self)


    @property
    def role_name(self):
        """
        Define a 'role_name' property for Atspi object.
        """
        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_role_name(self)


    @property
    def description(self):
        """
        Define a 'description' property for Atspi object.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_description(self)


    @property
    def parent(self):
        """
        Define a 'parent' property for Atspi object.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_parent(self)


    @property
    def index_in_parent(self):
        """
        Define a 'index_in_parent' property for Atspi object.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_index_in_parent(self)


    @property
    def attributes(self):
        """
        Define a 'attributes' property for Atspi object.
        """

        return AccessibleObject.get_attributes(self)


    @property
    def attributes_as_array(self):
        """
        Define a 'attributes_as_array' property for Atspi object.
        """

        return AccessibleObject.get_attributes_as_array(self)


    @property
    def children(self):
        """
        Creating children easy navigation when required.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_children(self)


    @property
    def dead(self):
        """
        Is the node dead (defunct)?
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.is_dead(self)


    def child(self, name=None, role_name=None, description=None, label=None, **kwargs):
        """
        Find a single child satisfying the name role_name or description.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        using_identifier = None
        using_role_name = role_name
        # === Backward compatibility and extra parameters ===
        for key, val in kwargs.items():
            if "roleName" in str(key):
                using_role_name = val

            if "identifier" in str(key):
                using_identifier = val
        # ===================================================

        predicate = GenericPredicate(
            name=name,
            role_name=using_role_name,
            description=description,
            label=label,
            identifier=using_identifier
        )

        return AccessibleObject.find_descendant(self, predicate, **kwargs)


    def is_child(self, name=None, role_name=None, description=None, label=None, **kwargs):
        """
        Determines whether a child satisfying the given criteria exists.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        using_identifier = None
        using_role_name = role_name
        # === Backward compatibility and extra parameters ===
        for key, val in kwargs.items():
            if "roleName" in str(key):
                using_role_name = val

            if "identifier" in str(key):
                using_identifier = val
        # ===================================================

        predicate = GenericPredicate(
            name=name,
            role_name=using_role_name,
            description=description,
            label=label,
            identifier=using_identifier
        )

        # Execute the search.
        try:
            # We do not care about a result here, just existence.
            AccessibleObject.find_descendant(self, predicate, **kwargs)
            return True
        except SearchError:
            return False


    def find_ancestor(self, predicate, **kwargs):
        """
        Find a single ancestor satisfying the predicate.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.find_ancestor(self, predicate, **kwargs)


    def find_child(self, predicate, **kwargs):
        """
        Find a single child satisfying the predicate.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.find_descendant(self, predicate, **kwargs)


    def find_children(self, predicate, **kwargs):
        """
        Find a all children satisfying the predicate.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.find_all_descendants(self, predicate, **kwargs)


    @property
    def last_child(self):
        """
        Is this Accessible Node the last child in parent node?
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.is_last_child(self)


    @property
    def child_count(self):
        """
        Get how many children Accessible Node has.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_child_count(self)


    @property
    def labeler(self):
        """
        'labeller' (read-only list of Node instances):
        The node(s) that is/are a label for this node. Generated from 'relations'.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_labeler(self)


    @property
    def labelee(self):
        """
        'labelee' (read-only list of Node instances):
        The node(s) that this node is a label for. Generated from 'relations'.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_labelee(self)


    def click(self, button=1, offset_x=0, offset_y=0):
        """
        Generates a raw mouse click event, using the specified button.
        - 1 is left,
        - 2 is middle,
        - 3 is right.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        click_x = int(self.position[0] + self.size[0] / 2) + offset_x
        click_y = int(self.position[1] + self.size[1] / 2) + offset_y

        # Starting with no workarounds for any role names or objects.
        # If something will start crashing we can fix it easily.

        click(click_x, click_y, button, window_id=self.window_id)


    def double_click(self, button=1, offset_x=0, offset_y=0):
        """
        Generates a raw mouse double-click event, using the specified button.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        click_x = int(self.position[0] + self.size[0] / 2) + offset_x
        click_y = int(self.position[1] + self.size[1] / 2) + offset_y

        # Starting with no workarounds for any role names or objects.
        # If something will start crashing we can fix it easily.

        double_click(click_x, click_y, button, window_id=self.window_id)


    def point(self, offset_x=0, offset_y=0):
        """
        Move mouse cursor to the center of the widget.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        point_x = int(self.position[0] + self.size[0] / 2) + offset_x
        point_y = int(self.position[1] + self.size[1] / 2) + offset_y

        # Starting with no workarounds for any role names or objects.
        # If something will start crashing we can fix it easily.

        point(point_x, point_y, window_id=self.window_id)


    def dump(self, output_type="plain", file_name=None, labels=False):
        """
        Dumping a structure representation.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        from dogtail.dump import AccessibleStructureRepresentation

        if output_type == "plain":
            print(AccessibleStructureRepresentation(self, "plain", file_name=file_name, labels=labels))

        elif output_type == "verbose":
            print(AccessibleStructureRepresentation(self, "verbose", file_name=file_name, labels=labels))

        elif output_type == "tree":
            # Print done by tree method.
            self.tree(file_name=file_name, labels=labels)

        else:
            LOGGING.info(f"Unknown output type: '{output_type}'")


    def tree(self, file_name=None, labels=False):
        """
        Dumping a tree structure of the node in tree like representation.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        from dogtail.dump import AccessibleStructureRepresentation

        print(AccessibleStructureRepresentation(self, "tree", file_name=file_name, labels=labels))


    def blink(self):
        """
        Blink will highlight the current node on the screen. Using Blinker from utility.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not self.extents:
            return False

        #from dogtail.utils import Blinker
        #(x, y, w, h) = self.extents
        #Blinker(x, y, w, h)
        return True


    @staticmethod
    def application(application_name):
        """
        Gets an application by name, returning an Application instance or raising an
        exception.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleRoot.application(application_name)


    @staticmethod
    def applications():
        """
        Get all applications.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleRoot.applications()


    ########################################
    # Backwards compatibility definitions. #
    ########################################
    def __setupUserData(self): # pylint: disable=invalid-name
        """
        Setup user data dictionary.
        """
        try:
            len(self.user_data)
        except (AttributeError, TypeError):
            self.user_data = {} # pylint: disable=attribute-defined-outside-init


    @property
    def debugName(self): # pylint: disable=invalid-name
        """
        Debug name assigned during search operations.
        """

        self.__setupUserData()
        return self.user_data.get("debugName", None)


    @debugName.setter
    def debugName(self, debugName): # pylint: disable=invalid-name
        """
        Debug name setter.
        """

        self.__setupUserData()
        self.user_data["debugName"] = debugName


    @property
    def combovalue(self):
        """
        The value (as a string) currently selected in the combo box.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return self.name


    @combovalue.setter
    def combovalue(self, value):
        """
        Set the value (as a string) in the combo box.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        self.childNamed(childName=value).doActionNamed("click")
        do_delay()


    @property
    def isChecked(self): # pylint: disable=invalid-name
        """
        Is the Accessible a checked checkbox? Compatibility property, same as
        Node.checked.
        """

        return self.checked


    @property
    def isSelected(self): # pylint: disable=invalid-name
        """
        Is the Accessible selected?
        """

        return self.selected


    @property
    def selectedChildren(self): # pylint: disable=invalid-name
        """
        Returns a list of children that are selected.
        """

        selected_children = []
        for index in range(AccessibleSelection.get_n_selected_children(self)):
            selected_children.append(AccessibleSelection.get_selected_child(self, index))
        return selected_children


    @property
    def roleName(self): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.role_name.
        """

        return self.role_name


    @property
    def minValue(self): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.min_value.
        """

        return self.min_value


    @property
    def maxValue(self): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.max_value.
        """

        return self.max_value


    @property
    def minValueIncrement(self): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.min_value_increment.
        """

        return self.min_value_increment


    def doActionNamed(self, named_action): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.do_action_named.
        """

        return self.do_action_named(named_action)


    def grabFocus(self): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.grab_focus.
        """

        return self.grab_focus()


    @property
    def indexInParent(self): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.index_in_parent.
        """

        return self.index_in_parent


    def isChild(self, name=None, roleName=None, description=None, label=None, **kwargs): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.is_child.
        """

        return self.is_child(
            name=name,
            role_name=roleName,
            description=description,
            label=label,
            **kwargs
        )


    def menu(self, menuName, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a menu with the given name.
        """

        return self.find_child(
            IsAMenuNamed(name=menuName),
            recursive=recursive,
            showing_only=showingOnly
        )


    def menuItem(self, menuItemName, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a menu item with the given name.
        """

        return self.find_child(
            IsAMenuItemNamed(name=menuItemName),
            recursive=recursive,
            showing_only=showingOnly
        )


    def textentry(self, textEntryName, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a text entry with the given name.
        """

        return self.find_child(
            IsATextEntryNamed(name=textEntryName),
            recursive=recursive,
            showing_only=showingOnly
        )


    def button(self, buttonName, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a button with the given name.
        """

        return self.find_child(
            IsAButtonNamed(name=buttonName),
            recursive=recursive,
            showing_only=showingOnly
        )


    def childLabelled(self, labelText, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a child labelled with the given text.
        """

        return self.find_child(
            IsLabelledAs(label=labelText),
            recursive=recursive,
            showing_only=showingOnly
        )


    def childNamed(self, childName, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a child with the given name.
        """

        return self.find_child(
            IsNamed(name=childName),
            recursive=recursive,
            showing_only=showingOnly
        )


    def tab(self, childName, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a tab with the given name.
        """

        return self.find_child(
            IsATabNamed(name=childName),
            recursive=recursive,
            showing_only=showingOnly
        )


    def dialog(self, dialogName, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a tab with the given name.
        """

        return self.find_child(
            IsADialogNamed(name=dialogName),
            recursive=recursive,
            showing_only=showingOnly
        )


    def window(self, windowName, recursive=True, showingOnly=None): # pylint: disable=invalid-name
        """
        Search below this node for a tab with the given name.
        """

        return self.find_child(
            IsAWindowNamed(name=windowName),
            recursive=recursive,
            showing_only=showingOnly
        )


    def findAncestor(self, predicate, retry=True): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.find_ancestor.
        """

        return self.find_ancestor(predicate, retry=retry)


    def findChild(self, predicate, retry=True): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.find_child.
        """

        return self.find_child(predicate, retry=retry)


    def findChildren(self, predicate): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.find_children.
        """

        return self.find_children(predicate)


    def selectAll(self): # pylint: disable=invalid-name
        """
        Selects all children.
        """

        return self.select_all()


    def deselectAll(self): # pylint: disable=invalid-name
        """
        Deselects all children.
        """

        return self.deselect_all()

    def doubleClick(self, button=1): # pylint: disable=invalid-name
        """
        Make a double-click.
        """

        return self.double_click(button=button)


    @property
    def link(self): # pylint: disable=invalid-name
        """
        Get Link from HyperText object.
        """

        try:
            if AccessibleObject.is_newton(self):
                # TODO
                return None

            for link_index in Atspi.HyperText.get_n_links(self):
                return Atspi.HyperText.get_link(self, link_index)

        except (NotImplementedError, AttributeError) as error:
            raise RuntimeError from error


    @property
    def URI(self): # pylint: disable=invalid-name
        """
        Get Link Anchor from HyperLink object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        try:
            if AccessibleObject.is_newton(self):
                # TODO
                return None

            for link_index in Atspi.HyperText.get_n_links(self):
                link = Atspi.HyperText.get_link(self, link_index)
                for anchor_index in link.get_n_anchors(link_index):
                    return link.get_uri(self, anchor_index)

        except (NotImplementedError, AttributeError) as error:
            raise RuntimeError from error


    def satisfies(self, pred):
        """
        Does this node satisfy the given predicate?
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        assert isinstance(pred, GenericPredicate)
        return pred.satisfied_by_node(self)

    ###############################################
    # End of backwards compatibility definitions. #
    ###############################################


    def __len__(self):
        return AccessibleObject.get_child_count(self)


    def __getitem__(self, index):
        length = len(self)

        if index < 0:
            index = index + length

        if index < 0 or index >= length:
            raise IndexError

        return AccessibleObject.get_child_at_index(self, index)


    def __bool__(self):
        return self is not None


    def __nonzero__(self):
        return self is not None


    def __str__(self):
        try:
            return f"[ '{self.name}' | '{self.role_name}' | '{self.description}' ]"
        except Exception as error:
            return f"[Exception encountered]: {error}"


Atspi.Accessible.__bases__ = (
    Node,
) + Atspi.Accessible.__bases__


# Load desktop to the root variable.
try:
    root = AccessibleUtilities.get_desktop()
except Exception:
    LOGGING.info("Error: Accessible desktop is not visible. Is accessibility enabled?")


# The 'children' field on desktop is inherited Field from GObject.Object
# We are recoding this logic in DogtailAPI so that the Object
# in 'children' is Accessible instead of default [object].
try:
    del Atspi.Accessible.children
except AttributeError:
    # Might be already deleted.
    pass

# To keep the same keyword <keyword> we need to remove the Atspi.Accessible.<keyword>
# So that the API is forced to use DogtailAPI.<keyword> and we can adjust it for Newton
try:
    del Atspi.Accessible.parent
except AttributeError:
    # Might be already deleted.
    pass

try:
    del Atspi.Accessible.name
except AttributeError:
    # Might be already deleted.
    pass

try:
    del Atspi.Accessible.description
except AttributeError:
    # Might be already deleted.
    pass

try:
    del Atspi.Accessible.attributes
except AttributeError:
    # Might be already deleted.
    pass
