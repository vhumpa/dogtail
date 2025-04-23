#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# ruff: noqa: E501
# ruff: noqa: E402

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from dogtail.utils import do_delay
from dogtail.config import config
from dogtail.logging import logging_class

LOGGING = logging_class.logger

from dogtail.accessibles.accessible_object import AccessibleObject, SearchError


class AccessibleUtilities:
    """
    Utility class.
    Heavily inspired by Orca's AXUtilities.
    """

    @staticmethod
    def get_application(acc_object):
        """
        Returns the application object of an Accessible.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        try:
            if AccessibleObject.is_newton(acc_object):
                application = acc_object.get_application()
            else:
                application = Atspi.Accessible.get_application(acc_object)

        except Exception as error:
            LOGGING.debug(f"Error when getting application node: {error}")
            return None

        return application


    @staticmethod
    def get_toolkit(acc_object):
        """
        Return string description of the toolkit we are using.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        toolkit = {}
        application_object = AccessibleUtilities.get_application(acc_object)
        toolkit_name = AccessibleUtilities.get_toolkit_name(application_object)
        toolkit_version = AccessibleUtilities.get_toolkit_version(application_object)
        toolkit[toolkit_name] = toolkit_version

        return toolkit



    @staticmethod
    def get_toolkit_name(acc_object):
        """
        Returns the name of the toolkit.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        try:
            if AccessibleObject.is_newton(acc_object):
                toolkit_name = acc_object.get_toolkit_name()
            else:
                toolkit_name = Atspi.Accessible.get_toolkit_name(acc_object)

        except Exception as error:
            LOGGING.debug(f"Error when getting toolkit name: {error}")
            return None

        return toolkit_name


    @staticmethod
    def get_toolkit_version(acc_object):
        """
        Returns the name of the toolkit.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        try:
            if AccessibleObject.is_newton(acc_object):
                toolkit_version = acc_object.get_toolkit_version()
            else:
                toolkit_version = Atspi.Accessible.get_toolkit_version(acc_object)

        except Exception as error:
            LOGGING.debug(f"Error when getting toolkit name: {error}")
            return None

        return toolkit_version


    @staticmethod
    def get_desktop():
        """
        Returns the accessible desktop.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        try:
            # TODO, figure out how to tell if Newton is to be used.
            # For now pass None to is_newton.
            if AccessibleObject.is_newton(None):
                #desktop = Newton.get_desktop(0)
                desktop = None
            else:
                desktop = Atspi.get_desktop(0)

        except Exception as error:
            LOGGING.debug(f"Error when getting desktop from Atspi: {error}")
            return None

        return desktop


    @staticmethod
    def get_all_applications():
        """
        Returns a list of applications known to Atspi.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        desktop = AccessibleUtilities.get_desktop()
        if desktop is None:
            return []

        return list(AccessibleObject.iter_children(desktop))


    @staticmethod
    def get_application_named(application_name, retry=True):
        """
        Returns a list of applications known to Atspi.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        for number_of_attempts in range(config.search_cut_off_limit):
            if number_of_attempts >= config.search_warning_threshold:
                LOGGING.info(f"Searching again (attempt '{number_of_attempts}')")

            for application in AccessibleUtilities.get_all_applications():
                if application.get_name() == application_name:
                    return application

            if not retry:
                break

            do_delay(config.search_back_off_delay)

        raise SearchError(f"Application '{application_name}' was not found in desktop.")


    @staticmethod
    def is_application_in_desktop(application):
        """
        Returns true if app is known to Atspi.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        for child in AccessibleUtilities.get_all_applications():
            if child.get_name() == application:
                return True

        LOGGING.debug("Application is not in desktop.")
        return False


    @staticmethod
    def get_application_with_pid(pid):
        """
        Returns the accessible application with the specified pid.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        for application_object in AccessibleUtilities.get_all_applications():
            if AccessibleObject.is_newton(application_object):
                if application_object.get_process_id() == pid:
                    return application_object
            else:
                if Atspi.Accessible.get_process_id(application_object) == pid:
                    return application_object

        LOGGING.debug(f"Application with pid '{pid}' not in desktop.")

        return None
