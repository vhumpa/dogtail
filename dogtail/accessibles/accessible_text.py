#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
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


class AccessibleText:
    """
    Text class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def add_selection(acc_object, start_offset, end_offset):
        """
        Selects some text (adds a text selection) in an Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.add_selection(start_offset, end_offset)

        return Atspi.Text.add_selection(acc_object, start_offset, end_offset)


    @staticmethod
    def get_attribute_run(acc_object, offset, include_defaults):
        """
        Gets a set of attributes applied to a range of text from an Atspi.Text object,
        optionally including its 'default' attributes.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_attribute_run(offset, include_defaults)

        return Atspi.Text.get_attribute_run(acc_object, offset, include_defaults)


    @staticmethod
    def get_bounded_ranges(acc_object, x, y, width, height, coord_type, clip_type_x, clip_type_y):
        """
        Gets the ranges of text from an Atspi.Text object which lie within the bounds
        defined by (x, y) and (x+'width', y+'height').
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_bounded_ranges(
                x,
                y,
                width,
                height,
                coord_type,
                clip_type_x,
                clip_type_y
            )

        return Atspi.Text.get_bounded_ranges(
            acc_object,
            x,
            y,
            width,
            height,
            coord_type,
            clip_type_x,
            clip_type_y
        )


    @staticmethod
    def get_caret_offset(acc_object):
        """
        Gets the current offset of the text caret in an Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_caret_offset()

        return Atspi.Text.get_caret_offset(acc_object)


    @staticmethod
    def get_character_at_offset(acc_object, offset):
        """
        Gets the character at a given offset for an Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_character_at_offset(offset)

        return Atspi.Text.get_character_at_offset(acc_object, offset)


    @staticmethod
    def get_character_count(acc_object):
        """
        Gets the character count of an #AccessibleText object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_character_count()

        return Atspi.Text.get_character_count(acc_object)


    @staticmethod
    def get_character_extents(acc_object, offset, coord_type):
        """
        Gets a bounding box containing the glyph representing the character at a
        particular text offset. The returned values are meaningful only if the Text has
        both STATE_VISIBLE and STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_character_extents(offset, coord_type)

        return Atspi.Text.get_character_extents(acc_object, offset, coord_type)


    @staticmethod
    def get_default_attributes(acc_object):
        """
        Gets the default attributes applied to an Atspi.Text object. The text attributes
        correspond to CSS attributes where possible. The combination of this attribute
        set and the attributes reported by Atspi.Text.get_text_attributes describes the
        entire set of text attributes over a range.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_default_attributes()

        return Atspi.Text.get_default_attributes(acc_object)


    @staticmethod
    def get_n_selections(acc_object):
        """
        Gets the number of active non-contiguous selections for an Atspi.Text object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_n_selections()

        return Atspi.Text.get_n_selections(acc_object)


    @staticmethod
    def get_offset_at_point(acc_object, x, y, coord_type):
        """
        Gets the character offset into the text at a given point.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_offset_at_point(x, y, coord_type)

        return Atspi.Text.get_offset_at_point(acc_object, x, y, coord_type)


    @staticmethod
    def get_range_extents(acc_object, start_offset, end_offset, coord_type):
        """
        Gets the bounding box for text within a range in an Atspi.Text object.
        The returned values are meaningful only if the Text has both STATE_VISIBLE and
        STATE_SHOWING.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_range_extents(start_offset, end_offset, coord_type)

        return Atspi.Text.get_range_extents(acc_object,start_offset, end_offset, coord_type)


    @staticmethod
    def get_selection(acc_object, selection_num):
        """
        Gets the bounds of the selection_num-th active text selection for an Atspi.Text
        object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_selection(selection_num)

        return Atspi.Text.get_selection(acc_object, selection_num)


    @staticmethod
    def get_string_at_offset(acc_object, offset, granularity):
        """
        Gets a portion of the text exposed through an Atspi.Text according to a given
        offset and a specific granularity, along with the start and end offsets defining
        the boundaries of such a portion of text.

        If granularity is Atspi.TextGranularity.CHAR (0) the character at the offset is
        returned.

        If granularity is Atspi.TextGranularity.WORD (1) the returned string is from the
        word start at or before the offset to the word start after the offset.

        The returned string will contain the word at the offset if the offset is inside
        a word and will contain the word before the offset if the offset is not inside
        a word.

        If granularity is Atspi.TextGranularity.SENTENCE (2) the returned string is from
        the sentence start at or before the offset to the sentence start after the
        offset.

        The returned string will contain the sentence at the offset if the offset is
        inside a sentence and will contain the sentence before the offset if the offset
        is not inside a sentence.

        If granularity is Atspi.TextGranularity.LINE (3) the returned string is from the
        line start at or before the offset to the line start after the offset.

        If granularity is Atspi.TextGranularity.PARAGRAPH (4) the returned string is
        from the start of the paragraph at or before the offset to the start of the
        following paragraph after the offset.

        New in version 2.9.90.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_string_at_offset(offset, granularity)

        return Atspi.Text.get_string_at_offset(acc_object, offset, granularity)


    @staticmethod
    def get_text(acc_object, start_offset, end_offset):
        """
        Gets a range of text from an Atspi.Text object. The number of bytes in the
        returned string may exceed either end_offset or start_offset, since UTF-8 is a
        variable-width encoding.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_text(start_offset, end_offset)

        return Atspi.Text.get_text(acc_object, start_offset, end_offset)


    @staticmethod
    def get_text_after_offset(acc_object, offset, coord_type):
        """
        Gets delimited text from an Atspi.Text object which follows a given text offset.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_text_after_offset(offset, coord_type)

        return Atspi.Text.get_text_after_offset(acc_object, offset, coord_type)


    @staticmethod
    def get_text_at_offset(acc_object, offset, coord_type):
        """
        Gets delimited text from an Atspi.Text object which includes a given text
        offset.

        Deprecated since version 2.10. Use Atspi.Text.get_string_at_offset.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_text_at_offset(offset, coord_type)

        return Atspi.Text.get_text_at_offset(acc_object, offset, coord_type)


    @staticmethod
    def get_text_attribute_value(acc_object, offset, attribute_name):
        """
        Gets the value of a named attribute at a given offset.

        Deprecated since version 2.10: Use Atspi.Text.get_text_attribute_value instead.

        Note: The deprecation note what to use seems wrong.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_text_attribute_value(offset, attribute_name)

        return Atspi.Text.get_text_attribute_value(acc_object, offset, attribute_name)


    @staticmethod
    def get_text_attributes(acc_object, offset):
        """
        Gets the attributes applied to a range of text from an Atspi.Text object.
        The text attributes correspond to CSS attributes where possible.

        Deprecated since version 2.10: Use Atspi.Text.get_text_attributes instead.

        Note: The deprecation note what to use seems wrong.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_text_attributes(offset)

        return Atspi.Text.get_text_attributes(acc_object, offset)


    @staticmethod
    def get_text_before_offset(acc_object, offset, coord_type):
        """
        Gets delimited text from an Atspi.Text object which precedes a given text
        offset.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_text_before_offset(offset, coord_type)

        return Atspi.Text.get_text_before_offset(acc_object, offset, coord_type)


    @staticmethod
    def remove_selection(acc_object, selection_num):
        """
        De-selects a text selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.remove_selection(selection_num)

        return Atspi.Text.remove_selection(acc_object, selection_num)


    @staticmethod
    def scroll_substring_to(acc_object, start_offset, end_offset, coord_type):
        """
        Scrolls whatever container of the Atspi.Text text range so it becomes visible
        on the screen.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.scroll_substring_to(start_offset, end_offset, coord_type)

        return Atspi.Text.scroll_substring_to(acc_object, start_offset, end_offset, coord_type)


    @staticmethod
    def scroll_substring_to_point(acc_object, start_offset, end_offset, coord_type, x, y):
        """
        Scrolls whatever container of the Atspi.Text text range so it becomes visible
        on the screen at a given position.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.scroll_substring_to_point(
                start_offset,
                end_offset,
                coord_type,
                x,
                y
            )

        return Atspi.Text.scroll_substring_to_point(
            acc_object,
            start_offset,
            end_offset,
            coord_type,
            x,
            y
        )


    @staticmethod
    def set_caret_offset(acc_object, new_offset):
        """
        Moves the text caret to a given position.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.set_caret_offset(new_offset)

        return Atspi.Text.set_caret_offset(acc_object, new_offset)


    @staticmethod
    def set_selection(acc_object, selection_num, start_offset, end_offset):
        """
        Changes the bounds of an existing Atspi.Text text selection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.set_selection(selection_num, start_offset, end_offset)

        return Atspi.Text.set_selection(acc_object, selection_num, start_offset, end_offset)


    @staticmethod
    def get_all_text(acc_object):
        """
        Get a text from Atspi.Text object without a need to specify range.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_text(acc_object):
            LOGGING.debug("This object does not have Atspi.Text interface.")
            return None

        if AccessibleObject.is_newton(acc_object):
            length = acc_object.get_character_count()
        else:
            length = Atspi.Text.get_character_count(acc_object)

        if not length:
            return ""

        return AccessibleText.get_text(acc_object, 0, length)
