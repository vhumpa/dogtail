#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# ruff: noqa: E402

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessible_object import AccessibleObject


class AccessibleText:
    """
    Text class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_text(acc_object):
        """
        Define a 'text' property for Atspi object.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            length = acc_object.get_character_count()
        else:
            length = Atspi.Text.get_character_count(acc_object)

        if not length:
            return ""

        try:
            if AccessibleObject.is_newton(acc_object):
                result = acc_object.get_text(0, length)
            else:
                result = Atspi.Text.get_text(acc_object, 0, length)

        except Exception as error:
            LOGGING.debug(f"Error when getting text from Atspi: {error}")
            return ""

        return result


    @staticmethod
    def set_text(acc_object, content):
        """
        Define a 'text' setter for Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return False

        if AccessibleObject.is_newton(acc_object):
            current_object_interfaces = acc_object.get_interfaces()
        else:
            current_object_interfaces = Atspi.Accessible.get_interfaces(acc_object)

        if not AccessibleObject.is_editable_text(acc_object):
            LOGGING.debug(f"Not valid interface: {current_object_interfaces}")
            return False

        try:
            if AccessibleObject.is_newton(acc_object):
                return acc_object.set_text_contents(content)

            return Atspi.EditableText.set_text_contents(acc_object, content)


        except Exception as error:
            LOGGING.debug(f"Error when setting text to Atspi: {error}")
            return False
