#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-outside-toplevel
# pylint: disable=invalid-name
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# ruff: noqa: E402
# ruff: noqa: E501

import os
import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from dogtail.config import config
from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessibles.accessible_object import AccessibleObject

from dogtail.ponytail_helper import ponytail_helper

SESSION_TYPE = "x11"
if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
    SESSION_TYPE = "wayland"

COORD_TYPE_SCREEN = 0
COORD_TYPE_WINDOW = 1
COORD_TYPE_PARENT = 2

class AccessibleComponent:
    """
    Component class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def contains(acc_object, x_coordinate, y_coordinate, coordinate_type=None):
        """
        Queries whether a given Atspi.Component contains a particular point.

        Atspi.CoordType.SCREEN = 0
        Atspi.CoordType.WINDOW = 1
        Atspi.CoordType.PARENT = 2
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if coordinate_type not in (0, 1, 2, None):
            LOGGING.debug(f"Not a valid coordinate type '{coordinate_type}'.")
            return False

        # Provide an option for user to set their own coord type.
        if coordinate_type:
            valid_coord_type = coordinate_type

        else:
            if SESSION_TYPE == "x11":
                valid_coord_type = coordinate_type if coordinate_type else COORD_TYPE_SCREEN

            if SESSION_TYPE == "wayland":
                valid_coord_type = coordinate_type if coordinate_type else COORD_TYPE_WINDOW

        if not valid_coord_type:
            LOGGING.debug("Unexpected session type and coordinate type not provided.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.contains(
                acc_object,
                x_coordinate,
                y_coordinate,
                valid_coord_type
            )

        action_result = Atspi.Component.contains(
            acc_object,
            x_coordinate,
            y_coordinate,
            valid_coord_type
        )

        return action_result


    @staticmethod
    def get_accessible_at_point(acc_object, x_coordinate, y_coordinate, coordinate_type=None):
        """
        Gets the accessible child at a given coordinate within an Atspi.Component.

        Atspi.CoordType.SCREEN = 0
        Atspi.CoordType.WINDOW = 1
        Atspi.CoordType.PARENT = 2
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if coordinate_type not in (0, 1, 2, None):
            LOGGING.debug(f"Not a valid coordinate type '{coordinate_type}'.")
            return False

        # Provide an option for user to set their own coord type.
        if coordinate_type:
            valid_coord_type = coordinate_type

        else:
            if SESSION_TYPE == "x11":
                valid_coord_type = coordinate_type if coordinate_type else COORD_TYPE_SCREEN

            if SESSION_TYPE == "wayland":
                valid_coord_type = coordinate_type if coordinate_type else COORD_TYPE_WINDOW

        if not valid_coord_type:
            LOGGING.debug("Unexpected session type and coordinate type not provided.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_accessible_at_point(
                acc_object,
                x_coordinate,
                y_coordinate,
                valid_coord_type
            )

        action_result = Atspi.Component.get_accessible_at_point(
            acc_object,
            x_coordinate,
            y_coordinate,
            valid_coord_type
        )

        return action_result


    @staticmethod
    def get_alpha(acc_object):
        """
        Gets the opacity/alpha value of a component, if alpha blending is in use.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_alpha()

        return Atspi.Component.get_alpha(acc_object)


    @staticmethod
    def get_extents(acc_object):
        """
        Gets the bounding box of the specified Atspi.Component. The returned values are
        meaningful only if the Component has both STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            return None

        # Atspi.CoordType.SCREEN = 0
        # Atspi.CoordType.WINDOW = 1

        try:
            # First lets check if screen coordinates are valid.
            if AccessibleObject.is_newton(acc_object):
                acc_rect = acc_object.get_extents(COORD_TYPE_SCREEN)

            else:
                acc_rect = Atspi.Component.get_extents(acc_object, Atspi.CoordType.SCREEN)

            # If not, usually by being 0, 0 attempt to get window coordinates.
            if (acc_rect.x, acc_rect.y) == (0, 0):
                if AccessibleObject.is_newton(acc_object):
                    acc_rect = acc_object.get_extents(COORD_TYPE_WINDOW)
                else:
                    acc_rect = Atspi.Component.get_extents(acc_object, Atspi.CoordType.WINDOW)

            # Return the tuple of 4 value from Atspi.Rect
            return (acc_rect.x, acc_rect.y, acc_rect.width, acc_rect.height)

        except Exception as error:
            LOGGING.debug(f"Exception when getting position or size: '{error}'")
            return None


    @staticmethod
    def get_layer(acc_object):
        """
        Queries which layer the component is painted into, to help determine its
        visibility in terms of stacking order.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_layer()

        return Atspi.Component.get_layer(acc_object)


    @staticmethod
    def get_mdi_z_order(acc_object):
        """
        Queries the z stacking order of a component which is in the MDI or window layer.
        (Bigger z-order numbers mean nearer the top)
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_mdi_z_order()

        return Atspi.Component.get_mdi_z_order(acc_object)


    @staticmethod
    def get_position(acc_object):
        """
        A tuple containing the position of the Accessible: (x, y)
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return (-1, -1)

        # Atspi.CoordType.SCREEN = 0
        # Atspi.CoordType.WINDOW = 1

        # The variable 'position' is of type Atspi.Point.
        if AccessibleObject.is_newton(acc_object):
            position = acc_object.get_position(COORD_TYPE_SCREEN)
        else:
            position = Atspi.Component.get_position(acc_object, Atspi.CoordType.SCREEN)

        # Check if the toolkit is GTK4.
        gtk_value = acc_object.toolkit.get("GTK", None)
        if gtk_value and gtk_value[0] == "4":
            #gtk4_offset = (12, 12)
            gtk4_offset = config.gtk4Offset

            # Determine if *this* node is a part of a full-screen frame
            fullscreen_offset = (0, 0)  # No offset fullscreen, shadows or not!
            node = acc_object  # Assuming 'acc_object' is the current node
            try:
                from dogtail.utils import get_screen_resolution

                # Check resolution result first. Can be None with caching.
                resolution_result = get_screen_resolution()
                if resolution_result:
                    screen_width, _ = resolution_result

                while node:
                    if node.role_name == "frame":
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
                if AccessibleObject.is_newton(acc_object):
                    position = acc_object.get_position(COORD_TYPE_WINDOW)
                else:
                    position = Atspi.Component.get_position(acc_object, Atspi.CoordType.WINDOW)

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
                if AccessibleObject.is_newton(acc_object):
                    position = acc_object.get_position(COORD_TYPE_WINDOW)
                else:
                    position = Atspi.Component.get_position(acc_object, Atspi.CoordType.WINDOW)

                if (position.x, position.y) != (0, 0):
                    # Inserting values in init for point has been deprecated and ignored.
                    atspi_point = Atspi.Point()
                    atspi_point.x = position.x + gtk4_offset[0]
                    atspi_point.y = position.y + gtk4_offset[1]
                    position = atspi_point

        return (position.x, position.y)


    @staticmethod
    def get_size(acc_object):
        """
        A tuple containing the size of the Accessible: (w, h)
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return (-1, -1)


        if SESSION_TYPE == "wayland":
            if acc_object.role_name in ("window", "dialog", "frame"):
                ponytail_interface = ponytail_helper.get_ponytail_interface()

                window_list = ponytail_interface.window_list
                window_id = acc_object.window_id

                for window in window_list:
                    if window["id"] == window_id:
                        return (int(window["width"]), int(window["height"]))


        if AccessibleObject.is_newton(acc_object):
            atspi_point = acc_object.get_size()

        else:
            atspi_point = Atspi.Component.get_size(acc_object)

        return (atspi_point.x, atspi_point.y)


    @staticmethod
    def grab_focus(acc_object):
        """
        Grab focus.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        try:
            if AccessibleObject.is_newton(acc_object):
                return acc_object.grab_focus()

            return Atspi.Component.grab_focus(acc_object)
        except Exception as error:
            LOGGING.debug(f"Exception when grabbing focus: '{error}'")
            return False



    @staticmethod
    def scroll_to(acc_object, scroll_type):
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

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if scroll_type not in (0, 1, 2, 3, 4, 5, 6):
            LOGGING.debug(f"Not a valid scroll type '{scroll_type}'.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.scroll_to(scroll_type)

        return Atspi.Component.scroll_to(acc_object, scroll_type)


    @staticmethod
    def scroll_to_point(acc_object, coordinate_type, x_coordinate, y_coordinate):
        """
        Scrolls whatever container of the Atspi.Component object so it becomes visible
        on the screen at a given position.

        Atspi.CoordType.SCREEN = 0
        Atspi.CoordType.WINDOW = 1
        Atspi.CoordType.PARENT = 2
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if coordinate_type not in (0, 1, 2):
            LOGGING.debug(f"Not a valid coordinate type '{coordinate_type}'.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.scroll_to_point(coordinate_type, x_coordinate, y_coordinate)

        return Atspi.Component.scroll_to_point(acc_object, coordinate_type, x_coordinate, y_coordinate)


    @staticmethod
    def set_extents(acc_object, x_coordinate, y_coordinate, width, height, coordinate_type):
        """
        Moves and resizes the specified component.

        Atspi.CoordType.SCREEN = 0
        Atspi.CoordType.WINDOW = 1
        Atspi.CoordType.PARENT = 2
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if coordinate_type not in (0, 1, 2):
            LOGGING.debug(f"Not a valid coordinate type '{coordinate_type}'.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.set_extents(
                x_coordinate,
                y_coordinate,
                width,
                height,
                coordinate_type
            )

        return Atspi.Component.set_extents(
            acc_object,
            x_coordinate,
            y_coordinate,
            width,
            height,
            coordinate_type
        )


    @staticmethod
    def set_position(acc_object, x_coordinate, y_coordinate, coordinate_type):
        """
        Moves the component to the specified position.

        Atspi.CoordType.SCREEN = 0
        Atspi.CoordType.WINDOW = 1
        Atspi.CoordType.PARENT = 2
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if coordinate_type not in (0, 1, 2):
            LOGGING.debug(f"Not a valid coordinate type '{coordinate_type}'.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.set_position(
                x_coordinate,
                y_coordinate,
                coordinate_type
            )

        return Atspi.Component.set_position(
            acc_object,
            x_coordinate,
            y_coordinate,
            coordinate_type
        )


    @staticmethod
    def set_size(acc_object, width, height):
        """
        Resizes the specified component to the given pixel dimensions.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.set_extents(width, height)

        return Atspi.Component.set_extents(acc_object, width, height)


    @staticmethod
    def get_center(acc_object):
        """
        A tuple containing the the center of the Accessible: (x, y)
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return (-1, -1)

        # Getting it this way already checks for Newton, no check here needed.
        accessible_position = AccessibleComponent.get_position(acc_object)
        accessible_size = AccessibleComponent.get_size(acc_object)

        atspi_point = Atspi.Point()
        atspi_point.x = int(accessible_position[0] + accessible_size[0] / 2)
        atspi_point.y = int(accessible_position[1] + accessible_size[1] / 2)

        return (atspi_point.x, atspi_point.y)
