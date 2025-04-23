#!/usr/bin/python3
"""
Class for Atspi.Image.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
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

from dogtail.accessibles.accessible_object import AccessibleObject

SESSION_TYPE = "x11"
if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
    SESSION_TYPE = "wayland"

COORD_TYPE_SCREEN = 0
COORD_TYPE_WINDOW = 1
COORD_TYPE_PARENT = 2

class AccessibleImage:
    """
    Image class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_image_description(acc_object):
        """
        Gets the description of the image displayed in an Atspi.Image object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if not AccessibleObject.is_image(acc_object):
            LOGGING.debug("This object does not have Atspi.Image interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_image_description()

        return Atspi.Image.get_image_description(acc_object)


    @staticmethod
    def get_image_extents(acc_object, coordinate_type=None):
        """
        Gets the bounding box of the image displayed in a specified Atspi.Image
        implementor. The returned values are meaningful only if the Image has both
        STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if not AccessibleObject.is_image(acc_object):
            LOGGING.debug("This object does not have Atspi.Image interface.")
            return None

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

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_image_extents(valid_coord_type)

        return Atspi.Image.get_image_extents(acc_object, valid_coord_type)


    @staticmethod
    def get_image_locale(acc_object):
        """
        Gets the locale associated with an image and its textual representation.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if not AccessibleObject.is_image(acc_object):
            LOGGING.debug("This object does not have Atspi.Image interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_image_locale()

        return Atspi.Image.get_image_locale(acc_object)


    @staticmethod
    def get_image_position(acc_object, coordinate_type=None):
        """
        Gets the minimum x and y coordinates of the image displayed in a specified
        Atspi.Image implementor. The returned values are meaningful only if the Image
        has both STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if not AccessibleObject.is_image(acc_object):
            LOGGING.debug("This object does not have Atspi.Image interface.")
            return None

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

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_image_position(valid_coord_type)

        return Atspi.Image.get_image_position(acc_object, valid_coord_type)


    @staticmethod
    def get_image_size(acc_object):
        """
        Gets the size of the image displayed in a specified Atspi.Image object.
        The returned values are meaningful only if the Image has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if not AccessibleObject.is_image(acc_object):
            LOGGING.debug("This object does not have Atspi.Image interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_image_size()

        return Atspi.Image.get_image_size(acc_object)
