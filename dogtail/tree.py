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

from dogtail.logging import logging_class
LOGGING = logging_class.logger


from dogtail.accessible_actions import AccessibleActions
from dogtail.accessible_component import AccessibleComponent
from dogtail.accessible_object import AccessibleObject
from dogtail.accessible_root import AccessibleRoot
from dogtail.accessible_selection import AccessibleSelection
from dogtail.accessible_state import AccessibleState
from dogtail.accessible_text import AccessibleText
from dogtail.accessible_utilities import AccessibleUtilities
from dogtail.accessible_value import AccessibleValue

from dogtail.predicate import GenericPredicate
from dogtail.ponytail_helper import ponytail_helper
from dogtail.rawinput import click, point, double_click


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


    @property
    def toolkit(self):
        """
        Return string description of the toolkit we are using.
        """

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
    def children(self):
        """
        Creating children easy navigation when required.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.get_children(self)


    @property
    def text(self):
        """
        Define a 'text' property for Atspi object.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.get_text(self)


    @text.setter
    def text(self, content):
        """
        Define a 'text' setter for Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleText.set_text(self, content)


    @property
    def actions(self):
        """
        Get dictionary of actions.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.get_actions(self)


    def do_action_named(self, named_action):
        """
        Do an Action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleActions.do_action_named(self, named_action)


    def action_key_bind(self, named_action):
        """
        Get key bind of an action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        action_index = self.actions[named_action]

        return AccessibleActions.get_key_binding(self, action_index)


    def grab_focus(self):
        """
        Grab focus.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.grab_focus(self)


    @property
    def dead(self):
        """
        Is the node dead (defunct)?
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleObject.is_dead(self)


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
    def states(self):
        """
        Get states.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleState.get_accessible_states(self)


    @property
    def value(self):
        """
        Gets the current value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.get_current_value(self)


    @value.setter
    def value(self, new_value):
        """
        Gets the current value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.set_current_value(self, new_value)


    @property
    def min_value(self):
        """
        Gets the minimum allowed value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.get_minimum_value(self)

    @property
    def max_value(self):
        """
        Gets the maximum allowed value for an Atspi.Value.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.get_maximum_value(self)


    @property
    def min_value_increment(self):
        """
        Gets the minimum increment by which an Atspi.Value can be adjusted.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleValue.get_minimum_increment(self)


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
        except RuntimeError:
            return False


    def find_child(self, predicate, **kwargs):
        """
        Find a single child satisfying th predicate.
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


    @property
    def extents(self):
        """
        A tuple containing the location and size of the Accessible: (x, y, w, h).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_extents(self)


    @property
    def size(self):
        """
        A tuple containing the size of the Accessible: (w, h).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_size(self)


    @property
    def position(self):
        """
        A tuple containing the position of the Accessible: (x, y).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_position(self)


    @property
    def center(self):
        """
        A tuple containing the center of the Accessible: (x, y).
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleComponent.get_center(self)


    def select_all(self):
        """
        Selects all children.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.select_all(self)


    def deselect_all(self):
        """
        Deselects all children.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        return AccessibleSelection.deselect_all(self)


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

        return AccessibleObject.get_index(self, index)


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
