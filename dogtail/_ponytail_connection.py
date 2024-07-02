#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release. Ponytail handling.
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


class PonytailWrapper(metaclass=Singleton):
    """
    Simple Ponytail wrapper class to initiate ponytail and keep one instance of it.
    """

    # Initial state, no connection.
    __window_id = None

    __ponytail = None
    __already_initiated = False


    expected_packages = [
        "gnome-ponytail-daemon",
        "python3-gnome-ponytail-daemon"
    ]

    error_message = "\n".join((
        "Error in ponytail initiation might be cause by several reasons:",
        f"\t1) Packages '{str(expected_packages)}' are not installed.",
        "\t2) If installed the gnome-ponytail-daemon process might not be running.",
        "\t3) You are on the system that does not have GNOME Shell Introspection.",
    ))

    # Keep session as a variable.
    session_type = "x11"
    if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
        session_type = "wayland"


    def __init__(self):
        LOGGING.debug("DEBUG - Initiating ponytail.")

        # Only makes sense when running under Wayland.
        if self.session_type != "wayland":
            return

        # Do not initiate it if already done.
        if not self.__already_initiated:
            try:
                LOGGING.debug("Initiating ponytail.")
                LOGGING.debug("DEBUG - IMPORT.")
                from ponytail.ponytail import Ponytail
                LOGGING.debug("DEBUG - INIT.")
                self.__ponytail = Ponytail()
                sleep(0.1) # Prevent any race conditions.
                LOGGING.debug("DEBUG - DISCONNECT.")
                self.__ponytail.disconnect()
                sleep(0.1) # Prevent any race conditions.

                self.__already_initiated = True

            except Exception as error:
                LOGGING.debug(f"Error when initiating ponytail: '{error}'")
                LOGGING.debug(self.error_message)


    def get_ponytail_instance(self):
        """
        Get ponytail instance.
        """
        LOGGING.debug("DEBUG - get_ponytail_instance.")

        return self.__ponytail


    def ponytail_check_is_xwayland(self, window_id=None, window_list=None):
        """
        Detect Xwayland windows in order to use globals and recordMonitor
        """
        LOGGING.debug("DEBUG - ponytail_check_is_xwayland.")

        ponytail = self.get_ponytail_instance()

        # If there is not window_list, get it from ponytail.
        if window_list is None:
            window_list = ponytail.window_list

        # If window_id is integer return client type.
        if isinstance(window_id, int):
            LOGGING.debug("Return wanted window_id.")
            try:
                return int([x["client-type"] for x in window_list if x["id"] == window_id][0])
            except Exception:
                return window_id

        # If window_id is None, get window_id of focused window.
        if window_id is None:
            LOGGING.debug("Return focused window if no window_id was provided.")
            for window in window_list:
                if bool(window["has-focus"]):
                    return int(window["client-type"])

        # The window_id match was not successful, return window_if of gnome-shell: 0.
        LOGGING.debug("Return window_id 0 which is gnome-shell if no id is found.")
        return 0


    def ponytail_check_connection(self, window_id=None, input_source="mouse"):
        """
        Check ponytail connection.
        """
        LOGGING.debug("DEBUG - ponytail_check_connection.")

        ponytail = self.get_ponytail_instance()

        window_list = ponytail.window_list

        if (not isinstance(window_id, str)) and (window_list != []) and\
            window_id not in [x["id"] for x in window_list]:
            window_id = None

        LOGGING.debug("Checking if possibly connected window still exists.")

        if ponytail.connected and isinstance(ponytail.connected, int):
            if ponytail.connected not in [x["id"] for x in window_list]:
                LOGGING.debug("Disconnecting no longer open window.")
                ponytail.disconnect()
                sleep(1)
                LOGGING.debug("Done.")

        if input_source == "keyboard" and ponytail.connected is None:
            LOGGING.debug("Keyboard event, connecting monitor.")
            ponytail.connectMonitor()

        elif input_source == "keyboard" and ponytail.connected is not None:
            if window_id == "" and isinstance(ponytail.connected, int):
                LOGGING.debug("Keyboard event, monitor request, forcing monitor.")
                ponytail.disconnect()
                sleep(1)
                ponytail.connectMonitor()
            else:
                LOGGING.debug("Any window/monitor already connected for keyboard event.")

        else:
            LOGGING.debug("Mouse input event.")
            if self.ponytail_check_is_xwayland(window_id, window_list):
                window_id = ""

            if ponytail.connected is None and window_id is None:
                for window in window_list:
                    if bool(window["has-focus"]) is True:
                        ponytail.connectWindow(window["id"])
                        LOGGING.debug("Connected active window.")

            elif ponytail.connected is not None and window_id is None:
                LOGGING.debug("Re-connected active window.")
                for window in window_list:
                    if bool(window["has-focus"]) is True:
                        if ponytail.connected != window["id"]:
                            ponytail.disconnect()
                            sleep(1)
                            ponytail.connectWindow(window["id"])
                            LOGGING.debug("Re-connected active window.")

            elif ponytail.connected is None:
                if isinstance(window_id, int):
                    ponytail.connectWindow(window_id)
                    LOGGING.debug("Connected window by window_id.")

                elif isinstance(window_id, str):
                    ponytail.connectMonitor(window_id)
                    LOGGING.debug("Connected monitor (Xwayland?) by window_id.")

            elif ponytail.connected != window_id and isinstance(window_id, int):
                LOGGING.debug("Disconnecting window.")
                ponytail.disconnect()
                sleep(1.5)

                LOGGING.debug(f"Connected window: '{ponytail.connected}'.")
                LOGGING.debug(f"Reconnecting window: '{window_id}'.")
                ponytail.connectWindow(window_id)
                LOGGING.debug(f"Connected window: '{ponytail.connected}'.")

            elif ponytail.connected != window_id and isinstance(window_id, str):
                LOGGING.debug("Disconnecting monitor.")
                ponytail.disconnect()
                sleep(1)

                LOGGING.debug("Reconnecting monitor.")
                ponytail.connectMonitor()
                LOGGING.debug("Connected monitor.")

            elif ponytail.connected == window_id:
                LOGGING.debug("Window or monitor is already connected.")


    def get_window_id(self, accessible_object):
        """
        Get window_id.
        """
        LOGGING.debug("DEBUG - get_window_id.")

        LOGGING.debug(" ===== Verbose window_id handling ===== ")

        window_id_return_value = ""

        if accessible_object.session_type == "x11":
            window_id_return_value = None

        if self.__window_id is None:
            LOGGING.debug("Window id event.")

            window_list = self.__ponytail.window_list
            if len(window_list) == 0:
                sleep(0.1)
                window_list = self.__ponytail.window_list

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
                    self.__window_id = [
                        x["id"] for x in window_list if bool(x["has-focus"]) is True
                    ][0]
                    window_id_return_value = self.__window_id
                    break

                # Ancestors parent is an application and the application is gnome-shell.
                if (
                    ancestor.parent.role_name == "application"
                    and ancestor.parent.name == "gnome-shell"
                ):
                    window_id_return_value = ""
                    break

                # Ancestors parent is an application and ancestor is a window.
                if (
                    ancestor.parent.role_name == "application"
                    and ancestor.role_name == "window"
                    and ancestor.name == ""
                ):
                    self.__window_id = [
                        x["id"] for x in window_list if bool(x["has-focus"]) is True
                    ][0]
                    window_id_return_value = self.__window_id
                    break

                # Ancestors parent is an application and ancestors name is in the list.
                if ancestor.parent.role_name == "application" and ancestor.name in [
                    x["title"] for x in window_list
                ]:
                    self.__window_id = [
                        x["id"] for x in window_list if x["title"] == ancestor.name
                    ][0]
                    window_id_return_value = self.__window_id
                    break

                # Ancestors parent is an application.
                if ancestor.parent.roleName == "application":
                    self.__window_id = [
                        x["id"] for x in window_list if bool(x["has-focus"]) is True
                    ][0]
                    window_id_return_value = self.__window_id
                    break

        else:
            window_id_return_value = self.__window_id


        LOGGING.debug(" ===== End of window_id handling ====== ")
        return window_id_return_value


    def get_window_has_focus(self):
        """
        Check if window is focused.
        """
        LOGGING.debug("DEBUG - get_window_has_focus.")

        #Get current window_id.
        window_id = self.__window_id

        # Get window_list.
        window_list = self.__ponytail.window_list

        # Iterate through the window_list to see what window has focus.
        for window in window_list:
            if window["id"] == window_id and bool(window["has-focus"]) is True:
                return True

        return False
