#/usr/bin/python3
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

from dogtail.config import config
from dogtail.utils import do_delay

from dogtail.accessible_object import AccessibleObject

class AccessibleActions:
    """
    Action class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_n_actions(acc_object):
        """
        Get number of invocable actions.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_action(acc_object):
            LOGGING.debug("Accessible object does not have an Action interface.")
            return 0

        try:
            if AccessibleObject.is_newton(acc_object):
                invocable_actions = acc_object.get_n_actions()
            else:
                invocable_actions = Atspi.Action.get_n_actions(acc_object)
        except Exception as error:
            LOGGING.debug(f"Exception getting actions: '{error}'")
            return 0

        return invocable_actions


    @staticmethod
    def get_action_name(acc_object, index):
        """
        Get an invocable action located on index.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_action(acc_object):
            LOGGING.debug("Accessible object does not have an Action interface.")
            return 0

        try:
            if AccessibleObject.is_newton(acc_object):
                invocable_actions = acc_object.get_action_name(index)
            else:
                invocable_actions = Atspi.Action.get_action_name(acc_object, index)

        except Exception as error:
            LOGGING.debug(f"Exception getting actions: '{error}'")
            return 0

        return invocable_actions



    @staticmethod
    def get_actions(acc_object):
        """
        Dictionary of actions.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        actions = {}

        try:
            for action_index in range(AccessibleActions.get_n_actions(acc_object)):
                action_name = AccessibleActions.get_action_name(acc_object, action_index)
                actions[action_name] = action_index
        except Exception as error:
            LOGGING.debug(f"Exception when getting actions dictionary: '{error}'")

        return actions


    @staticmethod
    def do_action_named(acc_object, named_action):
        """
        Do an Action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not isinstance(named_action, str):
            LOGGING.debug("This function expects action name string.")
            return False

        if not AccessibleObject.is_action(acc_object):
            LOGGING.debug("Accessible object does not have an Action interface.")
            return False

        if named_action not in AccessibleActions.get_actions(acc_object):
            LOGGING.debug("Wanted action is not supported on wanted object.")
            return False

        try:
            action_to_do = AccessibleActions.get_actions(acc_object)[named_action]

            if AccessibleObject.is_newton(acc_object):
                return acc_object.do_action(acc_object, action_to_do)

            action_result = Atspi.Action.do_action(acc_object, action_to_do)

            do_delay(config.search_back_off_delay)

            return action_result

        except Exception as error:
            LOGGING.debug(f"Exception when executing a named action: '{error}'")
            return False


    @staticmethod
    def get_key_binding(acc_object, action_index):
        """
        Get keybindings to the action_index-th action.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_action(acc_object):
            LOGGING.debug("Accessible object does not have an Action interface.")
            return None

        try:
            if AccessibleObject.is_newton(acc_object):
                action_key_bind = acc_object.get_key_binding(action_index)
            else:
                action_key_bind = Atspi.Action.get_key_binding(acc_object, action_index)

        except Exception as error:
            LOGGING.debug(f"Exception getting action key bind: '{error}'")
            return None

        return action_key_bind
