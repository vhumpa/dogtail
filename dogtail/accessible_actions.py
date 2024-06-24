#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# ruff: noqa: E402
# ruff: noqa: E501

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

# TODO To be change to dogtail.logging before release.
from _logging import Logging
logging_class = Logging()
LOGGER = logging_class.logger

from accessible_object import AccessibleObject

class AccessibleActions:
    """
    Utility class.
    Heavily inspired by Orca's classes.
    """

    @staticmethod
    def get_n_actions(acc_object):
        """
        Get number of invocable actions.
        """

        if not AccessibleObject.is_action(acc_object):
            LOGGER.info("Accessible object does not have an Action interface.")
            return 0

        try:
            if AccessibleObject.is_newton(acc_object):
                invocable_actions = acc_object.get_n_actions()
            else:
                invocable_actions = Atspi.Action.get_n_actions(acc_object)
        except Exception as error:
            LOGGER.info(f"Exception getting actions: '{error}'")
            return 0

        return invocable_actions


    @staticmethod
    def get_action_name(acc_object, index):
        """
        Get an invocable action located on index.
        """

        if not AccessibleObject.is_action(acc_object):
            LOGGER.info("Accessible object does not have an Action interface.")
            return 0

        try:
            if AccessibleObject.is_newton(acc_object):
                invocable_actions = acc_object.get_action_name(index)
            else:
                invocable_actions = Atspi.Action.get_action_name(acc_object, index)

        except Exception as error:
            LOGGER.info(f"Exception getting actions: '{error}'")
            return 0

        return invocable_actions



    @staticmethod
    def get_actions(acc_object):
        """
        Dictionary of actions.
        """

        actions = {}

        try:
            for action_index in range(AccessibleActions.get_n_actions(acc_object)):
                action_name = AccessibleActions.get_action_name(acc_object, action_index)
                actions[action_name] = action_index
        except Exception as error:
            LOGGER.info(f"Exception when getting actions dictionary: '{error}'")

        return actions


    @staticmethod
    def do_action_named(acc_object, named_action):
        """
        Do an Action.
        """

        if not isinstance(named_action, str):
            LOGGER.info("This function expects action name string.")
            return False

        if not AccessibleObject.is_action(acc_object):
            LOGGER.info("Accessible object does not have an Action interface.")
            return False

        if named_action not in AccessibleActions.get_actions(acc_object):
            LOGGER.info("Wanted action is not supported on wanted object.")
            return False

        try:
            action_to_do = AccessibleActions.get_actions(acc_object)[named_action]

            if AccessibleObject.is_newton(acc_object):
                return acc_object.do_action(action_to_do)

            return Atspi.Action.do_action(action_to_do)

        except Exception as error:
            LOGGER.info(f"Exception when executing a named action: '{error}'")
            return False
