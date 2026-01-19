#!/usr/bin/python3
"""
Class for Atspi.EditableText.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
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


class AccessibleEditableText:
    """
    Editable Text class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def copy_text(acc_object, start_position=None, end_position=None):
        """
        Copies text from an Atspi.EditableText object into the system clipboard.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return False

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return False

        if not AccessibleObject.is_editable_text(acc_object):
            LOGGING.debug("This object does not have Atspi.EditableText interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            text_length = acc_object.get_character_count()
        else:
            text_length = Atspi.Text.get_character_count(acc_object)

        if isinstance(start_position, int) and isinstance(end_position, int):
            validated_start = start_position
            validated_end = end_position

        else:
            validated_start = 0
            validated_end = text_length

        if validated_start == validated_end:
            LOGGING.debug("There is nothing to copy, start and end are equal.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.copy_text(validated_start, validated_end)

        return Atspi.EditableText.copy_text(acc_object, validated_start, validated_end)


    @staticmethod
    def cut_text(acc_object, start_position=None, end_position=None):
        """
        Deletes text from an Atspi.EditableText object, copying the excised portion into
        the system clipboard.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return False

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return False

        if not AccessibleObject.is_editable_text(acc_object):
            LOGGING.debug("This object does not have Atspi.EditableText interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            text_length = acc_object.get_character_count()
        else:
            text_length = Atspi.Text.get_character_count(acc_object)

        if isinstance(start_position, int) and isinstance(end_position, int):
            validated_start = start_position
            validated_end = end_position

        else:
            validated_start = 0
            validated_end = text_length

        if validated_start == validated_end:
            LOGGING.debug("There is nothing to copy, start and end are equal.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.cut_text(validated_start, validated_end)

        return Atspi.EditableText.cut_text(acc_object, validated_start, validated_end)


    @staticmethod
    def delete_text(acc_object, start_position=None, end_position=None):
        """
        Deletes text from an Atspi.EditableText object, without copying the excised
        portion into the system clipboard.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return False

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return False

        if not AccessibleObject.is_editable_text(acc_object):
            LOGGING.debug("This object does not have Atspi.EditableText interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            text_length = acc_object.get_character_count()
        else:
            text_length = Atspi.Text.get_character_count(acc_object)

        if isinstance(start_position, int) and isinstance(end_position, int):
            validated_start = start_position
            validated_end = end_position

        else:
            validated_start = 0
            validated_end = text_length

        if validated_start == validated_end:
            LOGGING.debug("There is nothing to copy, start and end are equal.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.delete_text(validated_start, validated_end)

        return Atspi.EditableText.delete_text(acc_object, validated_start, validated_end)


    @staticmethod
    def insert_text(acc_object, text, position=0, length=0):
        """
        Inserts text into an Atspi.EditableText object. As with all character offsets,
        the specified position may not be the same as the resulting byte offset, since
        the text is in a variable-width encoding.

        Deliberately moving parameters around so that the text is first.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return False

        if not AccessibleObject.is_editable_text(acc_object):
            LOGGING.debug("This object does not have Atspi.EditableText interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.insert_text(position, text, length)

        return Atspi.EditableText.insert_text(acc_object, position, text, length)


    @staticmethod
    def paste_text(acc_object, position=None):
        """
        Inserts text from the system clipboard into an Atspi.EditableText object. As
        with all character offsets, the specified position may not be the same as the
        resulting byte offset, since the text is in a variable-width encoding.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return False

        if not AccessibleObject.is_editable_text(acc_object):
            LOGGING.debug("This object does not have Atspi.EditableText interface.")
            return False

        if isinstance(position, int):
            validated_position = position
        else:
            validated_position = 0

        if AccessibleObject.is_newton(acc_object):
            return acc_object.paste_text(validated_position)

        return Atspi.EditableText.paste_text(acc_object, validated_position)


    @staticmethod
    def set_text_contents(acc_object, new_contents):
        """
        Replace the entire text contents of an Atspi.EditableText object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return False

        if not AccessibleObject.is_editable_text(acc_object):
            LOGGING.debug("This object does not have Atspi.EditableText interface.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.set_text_contents(new_contents)

        return Atspi.EditableText.set_text_contents(acc_object, new_contents)
