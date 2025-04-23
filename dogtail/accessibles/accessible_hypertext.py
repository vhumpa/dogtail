#!/usr/bin/python3
"""
Class for Atspi.Hypertext.
"""

# pylint: disable=import-error
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=no-name-in-module
# ruff: noqa: E402

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi


from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.accessibles.accessible_object import AccessibleObject


class AccessibleHypertext:
    """
    Hypertext class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_link(acc_object, link_index):
        """
        Gets the Atspi.Hyperlink object at a specified index.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_hypertext(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_link(link_index)

        return Atspi.Hypertext.get_link(acc_object, link_index)


    @staticmethod
    def get_link_index(acc_object, character_offset):
        """
        Gets the index of the Atspi.Hyperlink object at a specified character offset.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_hypertext(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_link_index(character_offset)

        return Atspi.Hypertext.get_link_index(acc_object, character_offset)


    @staticmethod
    def get_n_links(acc_object):
        """
        Gets the total number of Atspi.Hyperlink objects that an Atspi.Hypertext
        implementor has.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_hypertext(acc_object):
            LOGGING.debug("Object is not valid Accessible.")
            return False

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_n_links()

        return Atspi.Hypertext.get_n_links(acc_object)
