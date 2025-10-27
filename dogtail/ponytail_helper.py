#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release. Ponytail handling.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=no-name-in-module
# ruff: noqa: E402
# ruff: noqa: E501

import os

from time import sleep

from dogtail.config import config
from dogtail.utils import do_delay

from dogtail.logging import logging_class
LOGGING = logging_class.logger


class Singleton(type):
    """
    Singleton class used as metaclass by :py:class:`logger.Logging`.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PonytailHelper(metaclass=Singleton):
    """
    Simple Ponytail wrapper class to initiate ponytail and keep one instance of it.
    """

    # Initial state, no connection.
    _window_id = None

    _ponytail_dbus_interface = None
    _already_initiated = False

    expected_packages = [
        "gnome-ponytail-daemon",
        "python3-gnome-ponytail-daemon"
    ]

    error_message = "\n".join((
        "\n",
        "Error in ponytail initiation might be cause by several reasons:",
        f"\t1) Packages '{str(expected_packages)}' are not installed.",
        "\t2) If installed, the gnome-ponytail-daemon process might not be running.",
        "\t3) You are on the system that does not have GNOME Shell Introspection.",
        "\n",
    ))

    # Keep session as a variable.
    session_type = "x11"
    if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
        session_type = "wayland"


    def __init__(self):
        LOGGING.debug(logging_class.get_func_params_and_values())

        # Only makes sense when running under Wayland.
        if self.session_type != "wayland":
            return

        # Do not initiate it if already done.
        # But make a check to see if self._ponytail_dbus_interface is valid.
        if not self._already_initiated or not self._ponytail_dbus_interface:
            try:
                LOGGING.debug("Initiating ponytail.")
                from ponytail.ponytail import Ponytail
                self._ponytail_dbus_interface = Ponytail()
                sleep(0.1) # Prevent any race conditions.
                self._ponytail_dbus_interface.disconnect()
                sleep(0.1) # Prevent any race conditions.

                self._already_initiated = True

            except Exception as error:
                LOGGING.info(f"Error when initiating ponytail: '{error}'")
                LOGGING.info(self.error_message)


    def get_ponytail_interface(self):
        """
        Get ponytail interface.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not self._ponytail_dbus_interface:
            raise RuntimeError(self.error_message)

        return self._ponytail_dbus_interface


    def ponytail_check_is_xwayland(self, window_id=None, window_list=None):
        """
        Detect Xwayland windows in order to use globals and recordMonitor.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        ponytail_interface = self.get_ponytail_interface()

        # If there is not window_list, get it from ponytail.
        if window_list is None:
            window_list = ponytail_interface.window_list

        # If window_id is integer return client type.
        if isinstance(window_id, int):
            LOGGING.debug("Return wanted window_id.")
            try:
                _window_id = int([x["client-type"] for x in window_list if x["id"] == window_id][0])
                LOGGING.debug(f"Returning: '{_window_id}'")
                return _window_id

            except Exception as error:
                LOGGING.debug(f"Exception in ponytail: '{error}'")
                return window_id

        # If window_id is None, get window_id of focused window.
        if window_id is None:
            LOGGING.debug("Return focused window if no window_id was provided.")
            for window in window_list:
                if bool(window["has-focus"]):
                    LOGGING.debug(f"Returning client-type '{window['client-type']}'.")
                    return int(window["client-type"])

        # The window_id match was not successful, return window_if of gnome-shell: 0.
        LOGGING.debug("Return window_id 0 which is gnome-shell if no id is found.")
        return 0


    def ponytail_check_connection(self, window_id=None, input_source="mouse"):
        """
        Check ponytail connection.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        ponytail_interface = self.get_ponytail_interface()

        window_list = ponytail_interface.window_list

        if (not isinstance(window_id, str)) and (window_list != []) and\
            window_id not in [x["id"] for x in window_list]:
            window_id = None

        LOGGING.debug("Checking if possibly connected window still exists.")

        if ponytail_interface.connected and isinstance(ponytail_interface.connected, int):
            if ponytail_interface.connected not in [x["id"] for x in window_list]:
                LOGGING.debug("Disconnecting no longer open window.")
                ponytail_interface.disconnect()
                sleep(1)
                LOGGING.debug("Done.")

        if input_source == "keyboard" and ponytail_interface.connected is None:
            LOGGING.debug("Keyboard event, connecting monitor.")
            # ponytail_interface.disconnect()
            # sleep(1)
            ponytail_interface.connectMonitor()

        elif input_source == "keyboard" and ponytail_interface.connected is not None:
            if window_id == "" and isinstance(ponytail_interface.connected, int):
                LOGGING.debug("Keyboard event, monitor request, forcing monitor.")
                ponytail_interface.disconnect()
                sleep(1)
                ponytail_interface.connectMonitor()

                #try:
                #    ponytail_interface.connectMonitor()
                #except Exception:
                #    ponytail_interface.disconnect()
                #    sleep(1)
                #    ponytail_interface.connectMonitor()

            else:
                LOGGING.debug("Any window/monitor already connected for keyboard event.")

        else:
            LOGGING.debug("Mouse input event.")
            if self.ponytail_check_is_xwayland(window_id, window_list):
                window_id = ""

            if ponytail_interface.connected is None and window_id is None:
                # There is a corner case when using unit tests.
                window_was_connected = False
                for window in window_list:
                    if bool(window["has-focus"]) is True:
                        # ponytail_interface.disconnect()
                        # sleep(1)
                        ponytail_interface.connectWindow(window["id"])
                        window_was_connected = True
                        LOGGING.debug(f"Connected active window '{window['id']}'.")

                # Attempt to connect monitor only in cases when window was not found.
                if not window_was_connected:
                    LOGGING.debug("No active window, connecting monitor.")
                    ponytail_interface.disconnect()
                    sleep(1)
                    ponytail_interface.connectMonitor()

            elif ponytail_interface.connected is not None and window_id is None:
                for window in window_list:
                    if bool(window["has-focus"]) is True:
                        if ponytail_interface.connected != window["id"]:
                            ponytail_interface.disconnect()
                            sleep(1)
                            ponytail_interface.connectWindow(window["id"])
                            LOGGING.debug("Re-connected active window.")

            elif ponytail_interface.connected is None:
                if isinstance(window_id, int):
                    # ponytail_interface.disconnect()
                    # sleep(1)
                    ponytail_interface.connectWindow(window_id)
                    LOGGING.debug("Connected window by window_id.")

                elif isinstance(window_id, str):
                    # ponytail_interface.disconnect()
                    # sleep(1)
                    ponytail_interface.connectMonitor(window_id)
                    LOGGING.debug("Connected monitor (Xwayland?) by window_id.")

            elif ponytail_interface.connected != window_id and isinstance(window_id, int):
                LOGGING.debug("Disconnecting window.")
                ponytail_interface.disconnect()
                sleep(1.5)

                LOGGING.debug(f"Connected window: '{ponytail_interface.connected}'.")
                LOGGING.debug(f"Reconnecting window: '{window_id}'.")
                ponytail_interface.connectWindow(window_id)
                LOGGING.debug(f"Connected window: '{ponytail_interface.connected}'.")

            elif ponytail_interface.connected != window_id and isinstance(window_id, str):
                LOGGING.debug("Disconnecting monitor.")
                ponytail_interface.disconnect()
                sleep(1)

                LOGGING.debug("Reconnecting monitor.")
                ponytail_interface.connectMonitor()
                LOGGING.debug("Connected monitor.")

            elif ponytail_interface.connected == window_id:
                LOGGING.debug("Window or monitor is already connected.")

        LOGGING.debug(f"Working with window_id: '{ponytail_interface.connected}'.")


    def get_window_id(self, accessible_object):
        """
        Get window_id.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        LOGGING.debug(" ===== Verbose window_id handling ===== ")

        window_id_return_value = ""

        if accessible_object.session_type == "x11":
            LOGGING.debug(f"Session type: '{accessible_object.session_type}'")
            window_id_return_value = None

        # Save window_list to work through.
        ponytail_interface = self.get_ponytail_interface()
        window_list = ponytail_interface.window_list
        if len(window_list) == 0:
            LOGGING.debug("Window list was empty, doing another attempt.")

            do_delay(config.action_delay)

            window_list = ponytail_interface.window_list

        if self._window_id is None:
            LOGGING.debug("Window id event.")

            for window in window_list:
                if "title" not in window.keys():
                    window["title"] = ""

            node = accessible_object
            parent_list = [node]
            while node.parent is not None:
                parent_list.append(node.parent)
                node = node.parent

            for ancestor in parent_list:
                # Ancestors parent is None
                if ancestor.parent is None:
                    window_list_node_with_focus = [x["id"] for x in window_list if bool(x["has-focus"])]
                    self._window_id = window_list_node_with_focus[0] if window_list_node_with_focus else None
                    window_id_return_value = self._window_id
                    break

                # Ancestors parent is an application and the application is gnome-shell.
                if (ancestor.parent.role_name == "application"and ancestor.parent.name == "gnome-shell"):
                    window_id_return_value = ""
                    break

                # Ancestors parent is an application and ancestor is a window.
                if (ancestor.parent.role_name == "application" and ancestor.role_name == "window" and ancestor.name == ""):
                    window_list_node_with_focus = [x["id"] for x in window_list if bool(x["has-focus"])]
                    self._window_id = window_list_node_with_focus[0] if window_list_node_with_focus else None
                    window_id_return_value = self._window_id
                    break

                # Ancestors parent is an application and ancestors name is in the list.
                if ancestor.parent.role_name == "application" and ancestor.name in [x["title"] for x in window_list]:
                    window_list_node_with_title = [x["id"] for x in window_list if x["title"] == ancestor.name]
                    self._window_id = window_list_node_with_title[0] if window_list_node_with_title else None
                    window_id_return_value = self._window_id
                    break

                # Ancestors parent is an application.
                if ancestor.parent.roleName == "application":
                    window_id_return_value = self._window_id
                    break

        # If user provides a window that is not focused, refocus.
        elif self._window_id is not None and not self.get_window_has_focus():
            LOGGING.debug("Attempt to do an action on unfocused window, refocusing.")
            window_list_node_with_focus = [x["id"] for x in window_list if bool(x["has-focus"])]
            self._window_id = window_list_node_with_focus[0] if window_list_node_with_focus else None
            window_id_return_value = self._window_id

        else:
            LOGGING.debug("Window ID provided.")
            window_id_return_value = self._window_id

        # Final check for focus on existing window.
        if window_id_return_value != "" and not self.get_window_has_focus():
            LOGGING.debug(f"Attempting to use window_id '{window_id_return_value}'")
            LOGGING.debug("Window ID provided led to unfocused window, refocusing.")
            window_list_node_with_focus = [x["id"] for x in window_list if bool(x["has-focus"])]
            self._window_id = window_list_node_with_focus[0] if window_list_node_with_focus else None
            window_id_return_value = self._window_id

        LOGGING.debug(f"Window ID to use '{window_id_return_value}'")
        LOGGING.debug(" ===== End of window_id handling ====== ")

        # Do not cache the value.
        self._window_id = None

        return window_id_return_value


    def get_window_has_focus(self):
        """
        Check if window is focused.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        #Get current window_id.
        window_id = self._window_id

        # Get window_list.
        ponytail_interface = self.get_ponytail_interface()
        window_list = ponytail_interface.window_list

        # Iterate through the window_list to see what window has focus.
        for window in window_list:
            if window["id"] == window_id and bool(window["has-focus"]) is True:
                return True

        return False

ponytail_helper = PonytailHelper()
