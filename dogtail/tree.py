#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# ruff: noqa: E402
# ruff: noqa: E501

import os

import gi
from time import sleep

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import warnings

warnings.filterwarnings("ignore", "g_object_unref")

# TODO To be change to dogtail.logging before release.
from _logging import logging_class
LOGGING = logging_class.logger


from accessible_actions import AccessibleActions
from accessible_component import AccessibleComponent
from accessible_object import AccessibleObject
from accessible_root import AccessibleRoot
from accessible_selection import AccessibleSelection
from accessible_state import AccessibleState
from accessible_text import AccessibleText
from accessible_utilities import AccessibleUtilities
from accessible_value import AccessibleValue

from _simple_predicate import SimplePredicate
from _ponytail_connection import PonytailWrapper
from rawinput import click, point, double_click
from config import read_config


class DogtailAPI(object):
    """
    Main dogtail API definition.
    """

    # Initial state, no connection.
    __window_id = None

    LOGGING.info("Initiating dogtail api.")

    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    configuration = read_config()

    # TODO remove
    # Find out if debug dogtail is set to True and log to console if so.
    LOGGING.info("Debugging dogtail to console? " + str(configuration["debug_dogtail"]))

    if configuration["debug_dogtail"]:
        LOGGING.info("Debugging dogtail to console.")
        logging_class.debug_to_console()

    event_listeners = {}

    # Keep session as a variable.
    session_type = "x11"
    if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
        session_type = "wayland"

    # I do not understand this well enough. TODO
    def register_event(self, client, *names):
        """
        Register an event listener.
        """

        try:
            listener = self.event_listeners[client]
        except Exception:
            self.event_listeners[client] = Atspi.EventListener.new(self._dummy_listener)
            listener = self.event_listeners[client]

        for name in names:
            # If Newton do X.
                # Newton.event_listener.register...
            # else: Do Atspi
            Atspi.EventListener.register(listener, name)


    # I do not understand this well enough. TODO
    def deregister_event(self, client, *names):
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


    # I do not understand this well enough. TODO
    def _dummy_listener(self):
        """
        I do not understand this well enough yet.
        """

        LOGGING.info("Dummy listener.")


    @property
    def get_toolkit(self):
        """
        Return string description of the toolkit we are using.
        """

        return AccessibleUtilities.get_toolkit()


    @property
    def window_id(self):
        """
        Return window id of a node.
        """

        if self.session_type == "x11":
            return None

        if self.__window_id is None:
            LOGGING.info("Window id event.")

            window_list = self.ponytail.window_list
            if len(window_list) == 0:
                sleep(0.1)
                window_list = self.ponytail.window_list

            for window in window_list:
                if "title" not in window.keys():
                    window["title"] = ""

            node = self
            parent_list = [node]
            while node.parent is not None:
                parent_list.append(node.parent)
                node = node.parent

            for ancestor in parent_list:
                # Ancestors parent is None
                if ancestor.parent is None:
                    self.__window_id = [
                        x["id"] for x in window_list if bool(x["has-focus"]) is True
                    ][0]
                    return self.__window_id

                # Ancestors parent is an application and the application is gnome-shell.
                elif (
                    ancestor.parent.role_name == "application"
                    and ancestor.parent.name == "gnome-shell"
                ):
                    return ""

                # Ancestors parent is an application and ancestor is a window.
                elif (
                    ancestor.parent.role_name == "application"
                    and ancestor.role_name == "window"
                    and ancestor.name == ""
                ):
                    self.__window_id = [
                        x["id"] for x in window_list if bool(x["has-focus"]) is True
                    ][0]
                    return self.__window_id

                # Ancestors parent is an application and ancestors name is in the list.
                elif ancestor.parent.role_name == "application" and ancestor.name in [
                    x["title"] for x in window_list
                ]:
                    self.__window_id = [
                        x["id"] for x in window_list if x["title"] == ancestor.name
                    ][0]
                    return self.__window_id

                # Ancestors parent is an application.
                elif ancestor.parent.roleName == "application":
                    self.__window_id = [
                        x["id"] for x in window_list if bool(x["has-focus"]) is True
                    ][0]
                    return self.__window_id

        else:
            return self.__window_id


    @property
    def window_has_focus(self):
        """
        Check if window is focused.
        """

        if self.session_type != "wayland":
            LOGGING.info("Ponytail is not used in non Wayland session.")
            return False

        window_id = self.window_id

        window_list = self.ponytail.window_list
        # Iterate through the window_list to see what window has focus.
        for window in window_list:
            if window["id"] == window_id and bool(window["has-focus"]) is True:
                return True

        return False


    @property
    def name(self):
        """
        Define a 'name' property for Atspi object.
        """

        return AccessibleObject.get_name(self)


    @property
    def role(self):
        """
        Define a 'role property for Atspi object.
        """

        return AccessibleObject.get_role(self)


    @property
    def role_name(self):
        """
        Define a 'role_name' property for Atspi object.
        """

        return AccessibleObject.get_role_name(self)


    @property
    def description(self):
        """
        Define a 'description' property for Atspi object.
        """

        return AccessibleObject.get_description(self)


    @property
    def parent(self):
        """
        Define a 'parent' property for Atspi object.
        """

        LOGGING.info("Accessing .parent property.")

        return AccessibleObject.get_parent(self)


    @property
    def index_in_parent(self):
        """
        Define a 'index_in_parent' property for Atspi object.
        """

        return AccessibleObject.get_index_in_parent(self)


    @property
    def children(self):
        """
        Creating children easy navigation when required.
        """

        return AccessibleObject.get_children(self)


    @property
    def text(self):
        """
        Define a 'text' property for Atspi object.
        """

        return AccessibleText.get_text(self)


    @text.setter
    def text(self, content):
        """
        Define a 'text' setter for Atspi.Text object.
        """

        return AccessibleText.set_text(self, content)


    @property
    def actions(self):
        """
        Dictionary of actions.
        """

        return AccessibleActions.get_actions(self)


    def do_action_named(self, named_action):
        """
        Do an Action.
        """

        return AccessibleActions.do_action_named(self, named_action)


    def grab_focus(self):
        """
        Grab focus.
        """

        return AccessibleComponent.grab_focus(self)


    @property
    def active(self):
        """
        Indicates this object can accept keyboard focus, which means all events
        resulting from typing on the keyboard will normally be passed to it when it has
        focus.
        """

        return AccessibleState.get_active(self)


    @property
    def focusable(self):
        """
        Indicates this object can accept keyboard focus, which means all events
        resulting from typing on the keyboard will normally be passed to it when it has
        focus.
        """

        return AccessibleState.get_focusable(self)


    @property
    def focused(self):
        """
        Indicates this object currently has the keyboard focus.
        """

        return AccessibleState.get_focused(self)


    @property
    def pressed(self):
        """
        Indicates this object is currently pressed.
        """

        return AccessibleState.get_pressed(self)


    @property
    def resizable(self):
        """
        Indicates the size of this object's size is not fixed.
        """

        return AccessibleState.get_resizable(self)


    @property
    def sensitive(self):
        """
        Indicates this object is sensitive, e.g. to user interaction.
        """

        return AccessibleState.get_sensitive(self)


    @property
    def showing(self):
        """
        Indicates this object, the object's parent, the object's parent's parent, and
        so on, are all 'shown' to the end-user, i.e. subject to “exposure” if blocking
        or obscuring objects do not interpose between this object and the top of the
        window stack.
        """

        return AccessibleState.get_showing(self)


    @property
    def visible(self):
        """
        Indicates this object is visible, e.g. has been explicitly marked for exposure
        to the user.
        """

        return AccessibleState.get_visible(self)


    @property
    def checked(self):
        """
        Indicates this object is currently checked.
        """

        return AccessibleState.get_checked(self)


    @property
    def checkable(self):
        """
        Indicates this object has the potential to be checked, such as a checkbox or
        toggle-able table cell.
        """

        return AccessibleState.get_checkable(self)


    @property
    def read_only(self):
        """
        Indicates that an object which is ENABLED and SENSITIVE has a value which can be
        read, but not modified, by the user.
        """

        return AccessibleState.get_read_only(self)


    @property
    def collapsed(self):
        """
        Indicates this object is collapsed.
        """

        return AccessibleState.get_collapsed(self)


    @property
    def editable(self):
        """
        Indicates the user can change the contents of this object.
        """

        return AccessibleState.get_editable(self)


    def get_states(self):
        """
        Get states.
        """

        return AccessibleState.get_accessible_states(self)


    @property
    def value(self):
        """
        Gets the current value for an Atspi.Value
        """

        return AccessibleValue.get_current_value(self)


    @value.setter
    def value(self, new_value):
        """
        Gets the current value for an Atspi.Value
        """

        return AccessibleValue.set_current_value(self, new_value)


    @property
    def min_value(self):
        """
        Gets the minimum allowed value for an Atspi.Value.
        """

        return AccessibleValue.get_minimum_value(self)

    @property
    def max_value(self):
        """
        Gets the maximum allowed value for an Atspi.Value.
        """

        return AccessibleValue.get_maximum_value(self)


    @property
    def min_value_increment(self):
        """
        Gets the minimum increment by which an Atspi.Value can be adjusted.
        """

        return AccessibleValue.get_minimum_increment(self)


    def child(self, name=None, role_name=None, description=None, label=None, **kwargs):
        """
        Find a single child satisfying the name role_name or description.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        # === Backward compatibility for 'roleName' usage ===
        using_role_name = role_name

        for key, val in kwargs.items():
            if "roleName" in str(key).lower():
                using_role_name = val
        # =================================================

        predicate = SimplePredicate(
            name=name,
            role_name=using_role_name,
            description=description,
            label=label
        )

        return AccessibleObject.find_descendant(self, predicate.satisfied_by_node)


    def find_child(self, predicate):
        """
        Find a single child satisfying th predicate
        """

        result = None

        for _ in range(self.configuration["search_cut_off_limit"]):
            result = AccessibleObject.find_descendant(self, predicate)

            if result:
                break

        return result


    def find_children(self, predicate):
        """
        Find a all children satisfying th predicate
        """

        return AccessibleObject.find_all_descendants(self, predicate)


    @property
    def labeler(self):
        """
        'labeller' (read-only list of Node instances):
        The node(s) that is/are a label for this node. Generated from 'relations'.
        """

        return AccessibleObject.get_labeler(self)


    @property
    def labelee(self):
        """
        'labelee' (read-only list of Node instances):
        The node(s) that this node is a label for. Generated from 'relations'.
        """

        return AccessibleObject.get_labelee(self)


    @property
    def extents(self):
        """
        A tuple containing the location and size of the Accessible: (x, y, w, h)
        """

        return AccessibleComponent.get_extents(self)


    @property
    def size(self):
        """
        A tuple containing the size of the Accessible: (w, h)
        """

        return AccessibleComponent.get_size(self)


    @property
    def position(self):
        """
        A tuple containing the position of the Accessible: (x, y)
        """

        return AccessibleComponent.get_position(self)


    def select_all(self):
        """
        Selects all children.
        """

        return AccessibleSelection.select_all(self)


    def deselect_all(self):
        """
        Deselects all children.
        """

        return AccessibleSelection.deselect_all(self)


    def select(self):
        """
        Selects a child.
        """

        return AccessibleSelection.select(self)


    def deselect(self):
        """
        Deselects a child.
        """

        return AccessibleSelection.deselect(self)


    def click(self, button=1):
        """
        Generates a raw mouse click event, using the specified button.
        - 1 is left,
        - 2 is middle,
        - 3 is right.
        """

        click_x = int(self.position[0] + self.size[0] / 2)
        click_y = int(self.position[1] + self.size[1] / 2)

        # Starting with no workarounds for any role names or objects.
        # If something will start crashing we can fix it easily.

        click(click_x, click_y, button, window_id=self.window_id)


    def double_click(self, button=1):
        """
        Generates a raw mouse double-click event, using the specified button.
        """

        click_x = int(self.position[0] + self.size[0] / 2)
        click_y = int(self.position[1] + self.size[1] / 2)

        # Starting with no workarounds for any role names or objects.
        # If something will start crashing we can fix it easily.

        double_click(click_x, click_y, button, window_id=self.window_id)


    def point(self):
        """
        Move mouse cursor to the center of the widget.
        """

        point_x = int(self.position[0] + self.size[0] / 2)
        point_y = int(self.position[1] + self.size[1] / 2)

        # Starting with no workarounds for any role names or objects.
        # If something will start crashing we can fix it easily.

        point(point_x, point_y, window_id=self.window_id)


    def dump(self, output_type="plain", file_name=None):
        """
        Dumping a tree structure of the node.
        """

        from dogtail import _dump

        dumper = getattr(_dump, output_type)
        dumper(self, file_name)


    def blink(self):
        """
        Blink will highlight the current node on the screen. Using Blinker from utility.
        """

        if not self.extents:
            return False

        from dogtail._utils import Blinker
        (x, y, w, h) = self.extents
        Blinker(x, y, w, h)
        return True


    @staticmethod
    def application(application_name):
        """
        Gets an application by name, returning an Application instance or raising an
        exception.
        """

        return AccessibleRoot.application(application_name)


    @staticmethod
    def applications():
        """
        Get all applications.
        """

        return AccessibleRoot.applications()


    ########################################
    # Backwards compatibility definitions. #
    ########################################
    @property
    def roleName(self): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.role_name.
        """

        return self.role_name


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


    def findChild(self, predicate): # pylint: disable=invalid-name
        """
        For backwards compatibility reasons. Wrapper for self.find_child.
        """

        return self.find_child(predicate)


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
            return f"[{self.name} | {self.role_name} | {self.description}]"
        except Exception as error:
            return f"[Exception encountered]: {error}"


Atspi.Accessible.__bases__ = (
    DogtailAPI,
    AccessibleActions,
    AccessibleComponent,
    AccessibleObject,
    AccessibleRoot,
    AccessibleSelection,
    AccessibleState,
    AccessibleText,
    AccessibleUtilities,
    AccessibleValue,
) + Atspi.Accessible.__bases__


# Load desktop to the root variable.
try:
    root = AccessibleUtilities.get_desktop()
except Exception:  # pragma: no cover
    LOGGING.info("Error: Accessible desktop is not visible. Is accessibility enabled?")


# The 'children' field on desktop is inherited Field from GObject.Object
# We are recoding this logic in DogtailAPI so that the Object
# in 'children' is Accessible instead of default [object].
del Atspi.Accessible.children
# To keep the same keyword 'parent' we need to remove the Atspi.Accessible.parent
# So that the API is forced to use DogtailAPI.parent.
del Atspi.Accessible.parent
