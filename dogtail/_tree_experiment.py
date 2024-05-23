#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# ruff: noqa: E402

import gi
from types import LambdaType
from time import sleep

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import warnings

warnings.filterwarnings("ignore", "g_object_unref")

from qecore.logger import Logging
logging_class = Logging()
LOGGER = logging_class.logger

from _constants import SESSION_TYPE
from _simple_predicate import SimplePredicate
from _ponytail_connection import PonytailWrapper
from _rawinput import click, point, doubleClick


class DogtailAPI:
    """
    Main dogtail API definition.
    """

    # Initial state, no connection.
    __window_id = None

    LOGGER.info("Initiating dogtail api.")

    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()


    # Will become useful for checking if we do actions on Atspi or newton_atspi.
    @property
    def get_toolkit(self):
        """
        Return string description of the toolkit we are using.
        """

        toolkit = {}
        application_object = AccessibleUtilities.get_application(self)
        toolkit_name = AccessibleUtilities.get_toolkit_name(application_object)
        toolkit_version = AccessibleUtilities.get_toolkit_version(application_object)
        toolkit[toolkit_name] = toolkit_version

        return toolkit


    @property
    def window_id(self):
        """
        Return window id of a node.
        """

        if SESSION_TYPE == "x11":
            return None

        if self.__window_id is None:
            LOGGER.debug("Window id event.")

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

        if SESSION_TYPE != "wayland":
            LOGGER.info("Ponytail is not used in non Wayland session.")
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

        if not AccessibleObject.is_valid(self):
            return None

        return Atspi.Accessible.get_name(self)


    @property
    def role(self):
        """
        Define a 'role property for Atspi object.
        """

        if not AccessibleObject.is_valid(self):
            return None

        return Atspi.Accessible.get_role(self)


    @property
    def role_name(self):
        """
        Define a 'role_name' property for Atspi object.
        """

        if not AccessibleObject.is_valid(self):
            return None

        return Atspi.Accessible.get_role_name(self)


    @property
    def description(self):
        """
        Define a 'description' property for Atspi object.
        """

        if not AccessibleObject.is_valid(self):
            return None

        return Atspi.Accessible.get_description(self)


    @property
    def parent(self):
        """
        Define a 'parent' property for Atspi object.
        """

        if not AccessibleObject.is_valid(self):
            return None

        return Atspi.Accessible.get_parent(self)


    @property
    def index_in_parent(self):
        """
        Define a 'index_in_parent' property for Atspi object.
        """

        if not AccessibleObject.is_valid(self):
            return None

        # Default value if object has no containing parent or exception happened.
        final_index = -1

        # Not working as expected sometimes. Working around it.
        final_index = Atspi.Accessible.get_index_in_parent(self)
        if final_index == -1:
            LOGGER.info("Error in get_index_in_parent. Attempting to work around.")

            for index, child in enumerate(self.parent.children):
                if child.parent.get_child_at_index(index) == self:
                    LOGGER.info(f"Success, index was: '{index}'")
                    return index

        return final_index

    @property
    def children(self):
        """
        Creating children easy navigation when required.
        """

        children_list = []

        for index in range(AccessibleObject.get_child_count(self)):
            child = AccessibleObject.get_child_at_index(self, index)
            if child:
                children_list.append(child)

        return children_list


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
        return True


    def __nonzero__(self):
        return True


    def __str__(self):
        try:
            return f"[{self.name} | {self.role_name} | {self.description}]"
        except Exception as error:
            return f"[Exception encountered]: {error}"


    @property
    def text(self):
        """
        Define a 'text' property for Atspi object.
        """

        if not AccessibleObject.is_valid(self):
            return None

        length = Atspi.Text.get_character_count(self)
        if not length:
            return ""

        if not AccessibleObject.is_text(self):
            LOGGER.info("This object does not have Atspi.Text interface.")
            return ""

        try:
            result = Atspi.Text.get_text(self, 0, length)
        except Exception as error:
            LOGGER.info(f"Error when getting text from Atspi: {error}")
            return ""

        return result


    @text.setter
    def text(self, content):
        """
        Define a 'text' setter for Atspi.Text object.
        """

        if not AccessibleObject.is_valid(self):
            return False

        current_object_interfaces = Atspi.Accessible.get_interfaces(self)
        if not AccessibleObject.is_editable_text(self):
            LOGGER.info(f"Not valid interface: {current_object_interfaces}")
            return False

        try:
            return Atspi.EditableText.set_text_contents(self, content)
        except Exception as error:
            LOGGER.info(f"Error when setting text to Atspi: {error}")
            return False


    @property
    def actions(self):
        """
        Dictionary of actions.
        """

        actions = {}

        try:
            for action_index in range(AccessibleActions.get_n_actions(self)):
                action_name = AccessibleActions.get_action_name(self, action_index)
                actions[action_name] = action_index
        except Exception as error:
            LOGGER.info(f"Exception when getting actions dictionary: '{error}'")

        return actions


    def do_action_named(self, named_action):
        """
        Do an Action.
        """

        if not AccessibleObject.is_action(self):
            LOGGER.info("Accessible object does not have an Action interface.")
            return False

        if named_action not in self.actions:
            LOGGER.info("Wanted action is not supported on wanted object.")
            return False

        try:
            return Atspi.Action.do_action(self.actions[named_action])
        except Exception as error:
            LOGGER.info(f"Exception when executing a named action: '{error}'")
            return False


    def grab_focus(self):
        """
        Grab focus.
        """

        if not AccessibleObject.is_component(self):
            LOGGER.info("Accessible object does not have a Component interface.")
            return False

        try:
            return Atspi.Component.grab_focus(self)
        except Exception as error:
            LOGGER.info(f"Exception when grabbing focus: '{error}'")
            return False


    @property
    def active(self):
        """
        Indicates this object can accept keyboard focus, which means all events
        resulting from typing on the keyboard will normally be passed to it when it has
        focus.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.ACTIVE)


    @property
    def focusable(self):
        """
        Indicates this object can accept keyboard focus, which means all events
        resulting from typing on the keyboard will normally be passed to it when it has
        focus.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.FOCUSABLE)


    @property
    def focused(self):
        """
        Indicates this object currently has the keyboard focus.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.FOCUSED)


    @property
    def pressed(self):
        """
        Indicates this object is currently pressed.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.PRESSED)


    @property
    def resizable(self):
        """
        Indicates the size of this object's size is not fixed.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.RESIZABLE)


    @property
    def sensitive(self):
        """
        Indicates this object is sensitive, e.g. to user interaction.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.SENSITIVE)


    @property
    def showing(self):
        """
        Indicates this object, the object's parent, the object's parent's parent, and
        so on, are all 'shown' to the end-user, i.e. subject to “exposure” if blocking
        or obscuring objects do not interpose between this object and the top of the
        window stack.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.SHOWING)


    @property
    def visible(self):
        """
        Indicates this object is visible, e.g. has been explicitly marked for exposure
        to the user.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.VISIBLE)


    @property
    def checked(self):
        """
        Indicates this object is currently checked.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.CHECKED)


    @property
    def checkable(self):
        """
        Indicates this object has the potential to be checked, such as a checkbox or
        toggle-able table cell.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.CHECKABLE)


    @property
    def read_only(self):
        """
        Indicates that an object which is ENABLED and SENSITIVE has a value which can be
        read, but not modified, by the user.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.READ_ONLY)


    @property
    def collapsed(self):
        """
        Indicates this object is collapsed.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.COLLAPSED)


    @property
    def editable(self):
        """
        Indicates the user can change the contents of this object.
        """

        return Atspi.Accessible.get_state_set(self).contains(Atspi.StateType.EDITABLE)


    def get_states(self):
        """
        Get states.
        """

        return Atspi.StateSet.get_states(Atspi.Accessible.get_state_set(self))


    @property
    def value(self):
        """
        Gets the current value for an Atspi.Value
        """

        if not AccessibleObject.is_value(self):
            LOGGER.info("Accessible object does not have a Value interface.")
            return False

        return Atspi.Value.get_current_value(self)

    @value.setter
    def value(self, new_value):
        """
        Gets the current value for an Atspi.Value
        """

        if not AccessibleObject.is_value(self):
            LOGGER.info("Accessible object does not have a Value interface.")
            return False

        return Atspi.Value.set_current_value(new_value)


    @property
    def min_value(self):
        """
        Gets the minimum allowed value for an Atspi.Value.
        """

        if not AccessibleObject.is_value(self):
            LOGGER.info("Accessible object does not have a Value interface.")
            return False

        return Atspi.Value.get_minimum_value()


    @property
    def max_value(self):
        """
        Gets the maximum allowed value for an Atspi.Value.
        """

        if not AccessibleObject.is_value(self):
            LOGGER.info("Accessible object does not have a Value interface.")
            return False

        return Atspi.Value.get_maximum_value()


    @property
    def min_value_increment(self):
        """
        Gets the minimum increment by which an Atspi.Value can be adjusted.
        """

        if not AccessibleObject.is_value(self):
            LOGGER.info("Accessible object does not have a Value interface.")
            return False

        return Atspi.Value.get_minimum_increment()


    def child(self, name=None, role_name=None, description=None, label=None):
        """
        Find a single child satisfying the name role_name or description.
        """

        predicate = SimplePredicate(
            name=name,
            role_name=role_name,
            description=description,
            label=label
        )

        return AccessibleObject.find_descendant(self, predicate.satisfied_by_node)


    def find_child(self, pred):
        """
        Find a single child satisfying th predicate
        """

        # User is using lambdas.
        if isinstance(pred, LambdaType):
            predicate = pred
        # User is using a SimplePredicate.
        elif isinstance(pred, SimplePredicate):
            predicate = pred.satisfied_by_node
        # Unknown/unsupported way to compare nodes.
        else:
            LOGGER.info("Unknown/unsupported way to compare nodes.")
            return None

        result = None

        for _ in range(50): # CHANGE TO CONFIG NUMBER
            result = AccessibleObject.find_descendant(self, predicate)

            if result:
                break

        return result


    def find_children(self, pred):
        """
        Find a all children satisfying th predicate
        """

        # User is using lambdas.
        if isinstance(pred, LambdaType):
            predicate = pred
        # User is using a SimplePredicate.
        elif isinstance(pred, SimplePredicate):
            predicate = pred.satisfied_by_node
        # Unknown/unsupported way to compare nodes.
        else:
            LOGGER.info("Unknown/unsupported way to compare nodes.")
            return None

        return AccessibleObject.find_all_descendants(self, predicate)


    @property
    def labeler(self):
        """
        'labeller' (read-only list of Node instances):
        The node(s) that is/are a label for this node. Generated from 'relations'.
        """

        if not AccessibleObject.is_valid(self):
            return []

        targets = set()
        relation_set = Atspi.Accessible.get_relation_set(self)
        for relation in relation_set:
            if relation.get_relation_type() ==Atspi.RelationType.LABELLED_BY:
                if relation.get_n_targets() == 1:
                    return relation.get_target(0)

                # Using set to avoid duplicates.
                for i in range(relation.get_n_targets()):
                    targets.add(relation.get_target(i))
                return targets

        # Convert set to list.
        return list(targets)


    @property
    def labelee(self):
        """
        'labellee' (read-only list of Node instances):
        The node(s) that this node is a label for. Generated from 'relations'.
        """

        if not AccessibleObject.is_valid(self):
            return []

        targets = set()
        relation_set = Atspi.Accessible.get_relation_set(self)
        for relation in relation_set:
            if relation.get_relation_type() ==Atspi.RelationType.LABEL_FOR:
                if relation.get_n_targets() == 1:
                    return relation.get_target(0)

                # Using set to avoid duplicates.
                for i in range(relation.get_n_targets()):
                    targets.add(relation.get_target(i))
                return targets

        # Convert set to list.
        return list(targets)


    @property
    def extents(self):
        """
        A tuple containing the location and size of the Accessible: (x, y, w, h)
        """

        if not AccessibleObject.is_component(self):
            return None

        # Atspi.CoordType.SCREEN = 0
        # Atspi.CoordType.WINDOW = 1

        try:
            # First lets check if screen coordinates are valid.
            acc_rect = Atspi.Accessible.get_extents(self, Atspi.CoordType.SCREEN)

            # If not, usually by being 0, 0 attempt to get window coordinates.
            if (acc_rect.x, acc_rect.y) == (0, 0):
                acc_rect = Atspi.Accessible.get_extents(self, Atspi.CoordType.WINDOW)

            # Return the tuple of 4 value from Atspi.Rect
            return (acc_rect.x, acc_rect.y, acc_rect.width, acc_rect.height)

        except Exception as error:
            LOGGER.info(f"Exception when getting position or size: '{error}'")
            return None


    @property
    def size(self):
        """
        A tuple containing the size of the Accessible: (w, h)
        """

        if not AccessibleObject.is_component(self):
            LOGGER.info("Accessible object does not have a Component interface.")
            return (-1, -1)

        if SESSION_TYPE == "wayland":
            if self.role_name in ("window", "dialog", "frame"):
                window_list = self.ponytail.window_list
                window_id = self.window_id

                for window in window_list:
                    if window["id"] == window_id:
                        return (int(window["width"]), int(window["height"]))

        atspi_point = Atspi.Accessible.get_component_iface(self).get_size()
        return (atspi_point.x, atspi_point.y)


    @property
    def position(self):
        """
        A tuple containing the position of the Accessible: (x, y)
        """

        if not AccessibleObject.is_component(self):
            LOGGER.info("Accessible object does not have a Component interface.")
            return (-1, -1)


        # Atspi.CoordType.SCREEN = 0
        # Atspi.CoordType.WINDOW = 1

        # The variable position is of type Atspi.Point.
        comp_obj = Atspi.Accessible.get_component_iface(self)
        position = comp_obj.get_position(Atspi.CoordType.SCREEN)

        # Check if the toolkit is GTK4.
        if "GTK" in self.get_toolkit and self.get_toolkit["GTK"][0] == "4":
            #gtk4Offset = config.gtk4Offset TODO
            gtk4_offset = (12, 12)

            # Determine if *this* node is a part of a full-screen frame
            fullscreen_offset = (0, 0)  # No offset fullscreen, shadows or not!
            node = self  # Assuming 'self' is the current node
            try:
                from dogtail.utils import get_screen_resolution
                screen_width, _ = get_screen_resolution()
                while node:
                    if node.roleName == "frame":
                        frame_width, _ = node.size
                        if frame_width == screen_width:
                            gtk4_offset = fullscreen_offset
                        break
                    node = node.parent  # Traverse up to check for frame ancestors.
            except Exception:
                pass

            # For x11 session, calculate position using WINDOW_COORDS,
            # add up with window position and finally apply offset if not fullscreen.
            if SESSION_TYPE == "x11":
                # The variable position is of type Atspi.Point.
                position = comp_obj.get_position(Atspi.CoordType.WINDOW)

                from dogtail.utils import get_current_x_window_position
                base_x, base_y = get_current_x_window_position()
                # Add both gtk4_offset and the current x window position
                # Inserting values in init for point has been deprecated and ignored.
                atspi_point = Atspi.Point()
                atspi_point.x = position.x + base_x + gtk4_offset[0]
                atspi_point.y = position.y + base_y + gtk4_offset[1]
                position = atspi_point

            # For wayland.
            # If it's still (0, 0) return that otherwise do offset directly.
            if SESSION_TYPE == "wayland":
                position = comp_obj.get_position(Atspi.CoordType.WINDOW)
                if (position.x, position.y) != (0, 0):
                    # Inserting values in init for point has been deprecated and ignored.
                    atspi_point = Atspi.Point()
                    atspi_point.x = position.x + gtk4_offset[0]
                    atspi_point.y = position.y + gtk4_offset[1]
                    position = atspi_point

        # In future elif for newton will be required.
        # elif toolkit == newton:

        return (position.x, position.y)


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

        doubleClick(click_x, click_y, button, window_id=self.window_id)


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

        from dogtail import dump

        dumper = getattr(dump, output_type)
        dumper(self, file_name)


    def blink(self):
        """
        Blink will highlight the current node on the screen. Using Blinker from utility.
        """

        if not self.extents:
            return False

        from dogtail.utils import Blinker
        (x, y, w, h) = self.extents
        Blinker(x, y, w, h)
        return True


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


class Root:
    """
    Root class used to get data from Accessible.
    """

    def applications(self):
        """
        Get all applications.
        """

        return [x.get_name() for x in AccessibleUtilities.get_all_applications()]


    def application(self, application_name):
        """
        Gets an application by name, returning an Application instance or raising an
        exception.
        """

        return AccessibleUtilities.get_application_named(application_name)


class AccessibleSelection:
    """
    Utility class for Atspi.Selection.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def select_all(acc_obj):
        """
        Selects all children.
        """

        if not AccessibleObject.is_selection(acc_obj):
            LOGGER.info("This object does not have Atspi.Selection interface.")

        return Atspi.Selection.select_all(acc_obj)

    @staticmethod
    def deselect_all(acc_obj):
        """
        Deselects all children.
        """

        if not AccessibleObject.is_selection(acc_obj):
            LOGGER.info("This object does not have Atspi.Selection interface.")

        return Atspi.Selection.clear_selection(acc_obj)


    @staticmethod
    def select(acc_obj):
        """
        Selects a child.
        """

        if not AccessibleObject.is_selection(acc_obj):
            LOGGER.info("This object does not have Atspi.Selection interface.")

        parent = AccessibleObject.get_parent_checked(acc_obj)

        return Atspi.Selection.select_child(parent, acc_obj.get_index_in_parent())


    @staticmethod
    def deselect(acc_obj):
        """
        Deselects a child.
        """

        if not AccessibleObject.is_selection(acc_obj):
            LOGGER.info("This object does not have Atspi.Selection interface.")

        parent = AccessibleObject.get_parent_checked(acc_obj)

        return Atspi.Selection.deselect_child(parent, acc_obj.get_index_in_parent())


class AccessibleActions:
    """
    Utility class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_n_actions(acc_obj):
        """
        Get number of invocable actions.
        """

        if not AccessibleObject.is_action(acc_obj):
            LOGGER.info("Accessible object does not have an Action interface.")
            return 0

        try:
            invocable_actions = Atspi.Action.get_n_actions(acc_obj)
        except Exception as error:
            LOGGER.info(f"Exception getting actions: '{error}'")
            return 0

        return invocable_actions


    @staticmethod
    def get_action_name(acc_obj, index):
        """
        Get an invocable action located on index.
        """

        if not AccessibleObject.is_action(acc_obj):
            LOGGER.info("Accessible object does not have an Action interface.")
            return 0

        try:

            invocable_actions = Atspi.Action.get_action_name(acc_obj, index)
        except Exception as error:
            LOGGER.info(f"Exception getting actions: '{error}'")
            return 0

        return invocable_actions


class AccessibleUtilities:
    """
    Utility class.
    Heavily inspired by Orca's AXUtilities.
    """

    @staticmethod
    def get_application(acc_obj):
        """
        Returns the application object of an Accessible.
        """
        try:
            application = Atspi.Accessible.get_application(acc_obj)
        except Exception as error:
            LOGGER.info(f"Error when getting application node: {error}")
            return None

        return application


    @staticmethod
    def get_toolkit_name(acc_obj):
        """
        Returns the name of the toolkit.
        """

        try:
            toolkit_name = Atspi.Accessible.get_toolkit_name(acc_obj)
        except Exception as error:
            LOGGER.info(f"Error when getting toolkit name: {error}")
            return None

        return toolkit_name


    @staticmethod
    def get_toolkit_version(acc_obj):
        """
        Returns the name of the toolkit.
        """

        try:
            toolkit_version = Atspi.Accessible.get_toolkit_version(acc_obj)
        except Exception as error:
            LOGGER.info(f"Error when getting toolkit name: {error}")
            return None

        return toolkit_version

    @staticmethod
    def get_desktop():
        """
        Returns the accessible desktop.
        """

        try:
            desktop = Atspi.get_desktop(0)
        except Exception as error:
            LOGGER.info(f"Error when getting desktop from Atspi: {error}")
            return None

        return desktop


    @staticmethod
    def get_all_applications():
        """
        Returns a list of applications known to Atspi.
        """

        desktop = AccessibleUtilities.get_desktop()
        if desktop is None:
            return []

        return list(AccessibleObject.iter_children(desktop))


    @staticmethod
    def get_application_named(application_name):
        """
        Returns a list of applications known to Atspi.
        """

        for application in AccessibleUtilities.get_all_applications():
            if application.get_name() == application_name:
                return application

        LOGGER.info("Application was not found in desktop.")
        return None


    @staticmethod
    def is_application_in_desktop(application):
        """
        Returns true if app is known to Atspi.
        """

        for child in AccessibleUtilities.get_all_applications():
            if child.get_name() == application:
                return True

        LOGGER.info("Application is not in desktop.")
        return False

    @staticmethod
    def get_application_with_pid(pid):
        """
        Returns the accessible application with the specified pid.
        """

        for application in AccessibleUtilities.get_all_applications():
            if Atspi.Accessible.get_process_id(application) == pid:
                return application

        LOGGER.info(f"Application with pid '{pid}' not in desktop.")

        return None


class AccessibleObject:
    """
    Utility class for obtaining information about accessible objects.
    Heavily inspired by Orca's AXObject.
    """

    @staticmethod
    def is_valid(acc_object):
        """
        Returns False if we know for certain this object is invalid.
        """

        return acc_object is not None


    @staticmethod
    def is_action(acc_object):
        """
        Return True if Atspi object is an Action else False.
        """

        return Atspi.Accessible.get_action_iface(acc_object) is not None


    @staticmethod
    def is_text(acc_object):
        """
        Return True if Atspi object is an Text else False.
        """

        return Atspi.Accessible.get_text_iface(acc_object) is not None


    @staticmethod
    def is_editable_text(acc_object):
        """
        Return True if Atspi object is an EditableText else False.
        """

        return Atspi.Accessible.get_editable_text_iface(acc_object) is not None


    @staticmethod
    def is_component(acc_object):
        """
        Return True if Atspi object is a Component else False.
        """

        return Atspi.Accessible.get_component_iface(acc_object) is not None


    @staticmethod
    def is_selection(acc_object):
        """
        Return True if Atspi object is an EditableText else False.
        """

        return Atspi.Accessible.get_selection_iface(acc_object) is not None


    @staticmethod
    def is_value(acc_object):
        """
        Return True if Atspi object is an Value else False.
        """

        return Atspi.Accessible.get_value_iface(acc_object) is not None


    @staticmethod
    def iter_children(acc_obj, pred=None):
        """
        Generator to iterate through object's children. If the function pred is
        specified, children for which pred is False will be skipped.
        """

        if not AccessibleObject.is_valid(acc_obj):
            return

        child_count = AccessibleObject.get_child_count(acc_obj)
        for index in range(child_count):
            child = AccessibleObject.get_child_at_index(acc_obj, index)
            if child is not None and (pred is None or pred(child)):
                yield child

    @staticmethod
    def get_child_at_index(acc_obj, index):
        """
        Returns the nth child of obj.
        """

        if not AccessibleObject.is_valid(acc_obj):
            return None

        n_children = AccessibleObject.get_child_count(acc_obj)
        if n_children <= 0:
            return None

        if index == -1:
            index = n_children - 1

        if not 0 <= index < n_children:
            return None

        try:
            child = Atspi.Accessible.get_child_at_index(acc_obj, index)
        except Exception as error:
            LOGGER.info(f"Exception when getting child at index: '{error}'")
            return None

        if child == acc_obj:
            LOGGER.info(f"Object '{acc_obj}' claims to be its own child.")
            return None

        return child


    @staticmethod
    def get_child_count(acc_obj):
        """
        Returns number of children in given object.
        """

        if not AccessibleObject.is_valid(acc_obj):
            return 0

        try:
            count = Atspi.Accessible.get_child_count(acc_obj)
        except Exception as error:
            LOGGER.info(f"Exception when getting child count: '{error}'")
            return 0

        return count


    @staticmethod
    def _find_all_descendants(acc_object, predicate, matches):
        """
        Returns all descendants that match a predicate.
        """

        if not AccessibleObject.is_valid(acc_object):
            return

        child_count = AccessibleObject.get_child_count(acc_object)
        for index in range(child_count):
            child = AccessibleObject.get_child_at_index(acc_object, index)
            if predicate and predicate(child):
                matches.append(child)

            AccessibleObject._find_all_descendants(child, predicate, matches)


    @staticmethod
    def find_all_descendants(acc_obj, predicate):
        """
        Returns all descendants that match a predicate.
        """

        matches = []
        AccessibleObject._find_all_descendants(acc_obj, predicate, matches)
        return matches


    @staticmethod
    def find_descendant(obj, pred, depth_first=True):
        """
        Find a single descendant node satisfying the predicate.
        """

        if depth_first:
            success_match = AccessibleObject._find_descendant_depth_first(obj, pred)
        else:  # breadth_first
            success_match = AccessibleObject._find_descendant_breadth_first(obj, pred)

        return success_match


    @staticmethod
    def _find_descendant_depth_first(obj, pred):
        """
        Find a single descendant node satisfying the predicate, searching depth first.
        """

        try:
            if pred(obj):
                return obj
        except Exception:
            pass

        for child in obj:
            try:
                success_match = AccessibleObject._find_descendant_depth_first(child, pred)
            except Exception:
                success_match = None

            if success_match is not None:
                return success_match

        return


    @staticmethod
    def _find_descendant_breadth_first(obj, pred):
        """
        Find a single descendant node satisfying the predicate, searching breadth first.
        """

        for child in obj:
            try:
                if pred(obj):
                    return obj
            except Exception:
                pass

        for child in obj:
            try:
                success_match = AccessibleObject._find_descendant_breadth_first(child, pred)
            except Exception:
                success_match = None

            if success_match is not None:
                return success_match

        return


    @staticmethod
    def find_ancestor(obj, pred):
        """
        Find a single ancestor satisfying the predicate.
        """

        if not AccessibleObject.is_valid(obj):
            return None

        # Keep track of objects we've encountered in order to handle broken trees.
        objects = [obj]
        parent = AccessibleObject.get_parent_checked(obj)
        while parent:
            if parent in objects:
                LOGGER.info(f"Circular tree suspected, {parent} was found already.")
                return None

            if pred(parent):
                return parent

            objects.append(parent)
            parent = AccessibleObject.get_parent_checked(parent)

        return None


    @staticmethod
    def get_parent_checked(obj):
        """
        Returns the parent of obj, doing checks for tree validity.
        """

        if not AccessibleObject.is_valid(obj):
            return None

        role = obj.get_role
        if role in [Atspi.Role.INVALID, Atspi.Role.APPLICATION]:
            return None

        parent = obj.parent
        if parent is None:
            return None

        return parent



Atspi.Accessible.__bases__ = (
    DogtailAPI,
    Root,
    AccessibleActions,
    AccessibleObject,
    AccessibleUtilities,
) + Atspi.Accessible.__bases__


try:
    root = AccessibleUtilities.get_desktop()
except Exception:  # pragma: no cover
    LOGGER.info("Error: Accessible desktop is not visible. Is accessibility enabled?")
