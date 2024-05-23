#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release. Ponytail handling.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# ruff: noqa: E402

from time import sleep

from _constants import SESSION_TYPE

from qecore.logger import Logging  # noqa: E402
logging_class = Logging()
LOGGER = logging_class.logger


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

    expected_packages = [
        "gnome-ponytail-daemon",
        "python3-gnome-ponytail-daemon"
    ]

    error_message = "\n".join((
        "Error in ponytail initiation might be cause by several reasons:",
        f"1) Packages '{str(expected_packages)}' are not installed.",
        "2) If installed the gnome-ponytail-daemon process might not be running.",
        "3) You are on the system that does not have GNOME Shell Introspection.",
    ))

    __ponytail = None
    __already_initiated = False

    def __init__(self):
        # Only makes sense when running under Wayland.
        if SESSION_TYPE != "wayland":
            pass

        # Do not initiate it if already done.
        if not self.__already_initiated:
            try:
                LOGGER.info("Initiating ponytail.")
                from ponytail.ponytail import Ponytail
                self.__ponytail = Ponytail()
                sleep(0.1) # Prevent any race conditions.

                self.__ponytail.disconnect()
                sleep(0.1) # Prevent any race conditions.

                self.__already_initiated = True

            except Exception as error:
                LOGGER.info(f"Error when initiating ponytail: '{error}'")
                LOGGER.info(self.error_message)


    def get_ponytail_instance(self):
        """
        Get ponytail instance.
        """
        return self.__ponytail


def ponytail_check_is_xwayland(window_id=None, window_list=None):
    """
    Detect Xwayland windows in order to use globals and recordMonitor
    """

    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.ponytail

    # If there is not window_list, get it from ponytail.
    if window_list is None:
        window_list = ponytail.window_list

    # If window_id is integer return client type.
    if isinstance(window_id, int):
        LOGGER.debug("Return wanted window_id.")
        return int([x["client-type"] for x in window_list if x["id"] == window_id][0])

    # If window_id is None, get window_id of focused window.
    if window_id is None:
        LOGGER.debug("Return focused window if no window_id was provided.")
        for window in window_list:
            if bool(window["has-focus"]):
                return int(window["client-type"])

    # The window_id match was not successful, return window_if of gnome-shell: 0.
    LOGGER.debug("Return window_id 0 which is gnome-shell if no id is found.")
    return 0


def ponytail_check_connection(window_id=None, input_source="mouse"):
    """
    Check ponytail connection.
    """

    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.ponytail

    window_list = ponytail.window_list

    if (not isinstance(window_id, str)) and (window_list != []) and\
        window_id not in [x["id"] for x in window_list]:
        window_id = None

    LOGGER.debug("Checking if possibly connected window still exists.")

    if ponytail.connected and isinstance(ponytail.connected, int):
        if ponytail.connected not in [x["id"] for x in window_list]:
            LOGGER.debug("Disconnecting no longer open window.")
            ponytail.disconnect()
            sleep(1)
            LOGGER.debug("Done.")

    if input_source == "keyboard" and ponytail.connected is None:
        LOGGER.debug("Keyboard event, connecting monitor.")
        ponytail.connectMonitor()

    elif input_source == "keyboard" and ponytail.connected is not None:
        if window_id == "" and isinstance(ponytail.connected, int):
            LOGGER.debug("Keyboard event, monitor request, forcing monitor.")
            ponytail.disconnect()
            sleep(1)
            ponytail.connectMonitor()
        else:
            LOGGER.debug("Any window/monitor already connected for keyboard event.")

    else:
        LOGGER.debug("Mouse input event.")
        if ponytail_check_is_xwayland(window_id, window_list):
            window_id = ""

        if ponytail.connected is None and window_id is None:
            for window in window_list:
                if bool(window["has-focus"]) is True:
                    ponytail.connectWindow(window["id"])
                    LOGGER.debug("Connected active window.")

        elif ponytail.connected is not None and window_id is None:
            LOGGER.debug("Re-connected active window.")
            for window in window_list:
                if bool(window["has-focus"]) is True:
                    if ponytail.connected != window["id"]:
                        ponytail.disconnect()
                        sleep(1)
                        ponytail.connectWindow(window["id"])
                        LOGGER.debug("Re-connected active window.")

        elif ponytail.connected is None:
            if isinstance(window_id, int):
                ponytail.connectWindow(window_id)
                LOGGER.debug("Connected window by window_id.")

            elif isinstance(window_id, str):
                ponytail.connectMonitor(window_id)
                LOGGER.debug("Connected monitor (Xwayland?) by window_id.")

        elif ponytail.connected != window_id and isinstance(window_id, int):
            LOGGER.debug("Disconnecting window.")
            ponytail.disconnect()
            sleep(1.5)

            LOGGER.debug(f"Connected window: '{ponytail.connected}'.")
            LOGGER.debug(f"Reconnecting window: '{window_id}'.")
            ponytail.connectWindow(window_id)
            LOGGER.debug(f"Connected window: '{ponytail.connected}'.")

        elif ponytail.connected != window_id and isinstance(window_id, str):
            LOGGER.debug("Disconnecting monitor.")
            ponytail.disconnect()
            sleep(1)

            LOGGER.debug("Reconnecting monitor.")
            ponytail.connectMonitor()
            LOGGER.debug("Connected monitor.")

        elif ponytail.connected == window_id:
            LOGGER.debug("Window or monitor is already connected.")
