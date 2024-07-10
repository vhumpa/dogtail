#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
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

from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessible_object import AccessibleObject

SESSION_TYPE = "x11"
if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
    SESSION_TYPE = "wayland"

class AccessibleComponent:
    """
    Component class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def grab_focus(acc_object):
        """
        Grab focus.
        """

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
    def get_extents(acc_object):
        """
        A tuple containing the location and size of the Accessible: (x, y, w, h)
        """

        if not AccessibleObject.is_component(acc_object):
            return None

        # Atspi.CoordType.SCREEN = 0
        # Atspi.CoordType.WINDOW = 1
        COORD_TYPE_SCREEN = 0
        COORD_TYPE_WINDOW = 1

        try:
            # First lets check if screen coordinates are valid.
            if AccessibleObject.is_newton(acc_object):
                acc_rect = acc_object.get_extents(COORD_TYPE_SCREEN)

            else:
                acc_rect = Atspi.Accessible.get_extents(acc_object, Atspi.CoordType.SCREEN)

            # If not, usually by being 0, 0 attempt to get window coordinates.
            if (acc_rect.x, acc_rect.y) == (0, 0):
                if AccessibleObject.is_newton(acc_object):
                    acc_rect = acc_object.get_extents(COORD_TYPE_WINDOW)
                else:
                    acc_rect = Atspi.Accessible.get_extents(acc_object, Atspi.CoordType.WINDOW)

            # Return the tuple of 4 value from Atspi.Rect
            return (acc_rect.x, acc_rect.y, acc_rect.width, acc_rect.height)

        except Exception as error:
            LOGGING.debug(f"Exception when getting position or size: '{error}'")
            return None

    @staticmethod
    def get_size(acc_object):
        """
        A tuple containing the size of the Accessible: (w, h)
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return (-1, -1)


        if SESSION_TYPE == "wayland":
            if acc_object.role_name in ("window", "dialog", "frame"):
                window_list = acc_object.ponytail.window_list
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
    def get_position(acc_object):
        """
        A tuple containing the position of the Accessible: (x, y)
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_component(acc_object):
            LOGGING.debug("Accessible object does not have a Component interface.")
            return (-1, -1)

        # Atspi.CoordType.SCREEN = 0
        # Atspi.CoordType.WINDOW = 1
        COORD_TYPE_SCREEN = 0
        COORD_TYPE_WINDOW = 1

        # The variable 'position' is of type Atspi.Point.
        if AccessibleObject.is_newton(acc_object):
            position = acc_object.get_position(COORD_TYPE_SCREEN)
        else:
            position = Atspi.Component.get_position(acc_object, Atspi.CoordType.SCREEN)

        # Check if the toolkit is GTK4.
        if "GTK" in acc_object.get_toolkit and acc_object.get_toolkit["GTK"][0] == "4":
            #gtk4Offset = config.gtk4Offset TODO
            gtk4_offset = (12, 12)

            # Determine if *this* node is a part of a full-screen frame
            fullscreen_offset = (0, 0)  # No offset fullscreen, shadows or not!
            node = acc_object  # Assuming 'acc_object' is the current node
            try:
                from dogtail.utils import get_screen_resolution

                # This gets executed a lot, on every .position query.
                # The function is cashed in utils.py for better performance.
                # TODO make a check for return value.
                screen_width, _ = get_screen_resolution()

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
