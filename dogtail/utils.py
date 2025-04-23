#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
Various Utilities
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=no-name-in-module
# ruff: noqa: E402
# ruff: noqa: E501


from time import sleep
import os
import sys
import errno
import shlex
import subprocess
import functools

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk

from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.config import config


def do_delay(delay=None):
    """
    Utility function to insert a delay (with logging and a configurable default delay).
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    if delay is None:
        delay = config.default_delay
        LOGGING.debug(f"Default Delay: Sleeping for '{delay}'")

    if config.debug_sleep:
        LOGGING.debug(f"Debug Sleep: Sleeping for '{delay}'")

    sleep(float(delay))


def run(string, timeout=None, interval=None, desktop=None, dumb=False, app_name="", **kwargs,):
    """
    Runs an application.
    [For simple command execution such as 'rm *', use os.popen() or os.system()]
    If dumb is omitted or is False, polls at interval seconds until the application is finished
    starting, or until timeout is reached. If dumb is True, returns when timeout is reached.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # Users can change timeout and interval via config.ini or by parameter in function.
    validated_timeout = config.run_timeout if timeout is None else timeout
    validated_interval = config.run_interval if interval is None else interval

    # Use root if not desktop was given. Why desktop though? This is weird.
    if desktop is None:
        from dogtail.tree import root
    else:
        root = desktop

    args = shlex.split(string)
    os.environ["GTK_MODULES"] = "gail:atk-bridge"
    process = subprocess.Popen(args, env=os.environ)

    # === Backward compatibility for 'appName' usage ===
    validated_application_name = app_name
    for key, val in kwargs.items():
        if "appName" in str(key):
            validated_application_name = val
    # ==================================================
    if not validated_application_name:
        validated_application_name = args[0]

    if dumb:
        LOGGING.debug("Disable startup detection.")
        do_delay(validated_timeout)

    else:
        LOGGING.debug("Startup detection code.")

        time = 0

        while time < validated_timeout:
            time = time + validated_interval

            try:
                application = root.application(validated_application_name)
                assert application.child(role_name="frame")
                do_delay(validated_interval)
                return process

            except Exception:
                pass

            do_delay(validated_interval)

    return process


class Lock:
    """
    A known system-wide mutex implementation that uses atomicity of the mkdir operation
    in UNIX-like systems. This should be used mainly to provide mutual exclusion in
    handling possible collisions among multiple script instances. You can choose to make
    randomized single-script wise locks or a more general locks if you do not choose to
    randomize the lock dir name. Set unLockOnExit to True to enable automatic unlock
    when script process exits to avoid having to unlock manually.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    def __init__(
        self,
        location="/tmp",
        lockname="dogtail_lockdir_",
        randomize=True,
        unlock_on_exit=False,
        **kwargs,
    ):
        """
        You can change the default lockdir location or name. Setting randomize to
        False will result in no random string being appended to the lockdir name.
        """

        using_unlock_on_exit = unlock_on_exit
        # === Backward compatibility and extra parameters ===
        for key, val in kwargs.items():
            if "unlockOnExit" in str(key):
                using_unlock_on_exit = val
        # ===================================================

        self.lockdir = os.path.join(os.path.normpath(location), lockname)
        if randomize:
            self.lockdir = "".join((self.lockdir, self.__getPostfix()))

        self.unlock_on_exit = using_unlock_on_exit

    def __exit_unlock(self):
        """
        Removes the lock upon exiting headless.
        """

        #debug_log("Remove the lock. Raising the exception if the lock is not present.")

        if os.path.exists(self.lockdir):
            try:
                os.rmdir(self.lockdir)
            except OSError:
                pass  # already deleted (by .unlock()), we're exiting, it's fine

    def lock(self):
        """
        Creates a lockdir based on the settings on Lock() instance creation.
        Raises OSError exception of the lock is already present. Should be
        atomic on POSIX compliant systems.
        """

        LOGGING.debug(" ".join((
                "Create a lock directory."
                "Raising the exception if the lock is already present."
            ))
        )

        locked_msg = "Dogtail lock: Already locked with the same lock."

        if not os.path.exists(self.lockdir):
            try:
                os.mkdir(self.lockdir)
            except OSError as error:
                if error.errno == errno.EEXIST and os.path.isdir(self.lockdir):
                    raise OSError(locked_msg) from error

            if os.path.exists(self.lockdir):
                if self.unlockOnExit:
                    import atexit

                    atexit.register(self.__exit_unlock)

                return self.lockdir
        else:
            raise OSError(locked_msg)

    def unlock(self):
        """
        Removes a lock. Will raise OSError exception if the lock was not present.
        Should be atomic on POSIX compliant systems.
        """

        LOGGING.debug("Remove the lock. Raising the exception if the lock is not present.")

        if self.unlock_on_exit:
            raise RuntimeError("Cannot unlock with unlock_on_exit set to True!")

        if os.path.exists(self.lockdir):
            try:
                os.rmdir(self.lockdir)
            except OSError as error:
                if error.errno == errno.EEXIST:
                    raise OSError("Dogtail unlock: lockdir removed elsewhere!") from error
        else:
            raise OSError("Dogtail unlock: not locked")

    def locked(self):
        """
        Check if locked directory exists.
        """

        LOGGING.debug("Checking if locked directory exists.")

        return os.path.exists(self.lockdir)


    # More commonly used word as opposed to postfix.
    def __get_suffix(self):
        """
        Generate a length of 5 random string that serves as file name suffix.
        """

        import random
        import string

        LOGGING.debug("Get random file suffix of length 5.")

        return "".join(
            random.choice(string.ascii_letters + string.digits) for x in range(5)
        )


    ########################################
    # Backwards compatibility definitions. #
    ########################################
    def __getPostfix(self): # pylint: disable=invalid-name
        """
        Wrapper over __get_suffix.
        """

        return self.__get_suffix()

    @property
    def unlockOnExit(self): # pylint: disable=invalid-name
        """
        Making a property in case users would like to access it and change it.
        """

        return self.unlock_on_exit

    @unlockOnExit.setter
    def unlockOnExit(self, value_to_set): # pylint: disable=invalid-name
        """
        Setter for unlockOnExit.
        """

        assert isinstance(value_to_set, bool), "unlockOnExit has to be of type 'bool'."
        self.unlock_on_exit = value_to_set

    ###############################################
    # End of backwards compatibility definitions. #
    ###############################################


def bail_because_accessibility_is_disabled():
    """
    Accessibility is detected as enabled. End the execution if there are no exceptions.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    if sys.argv[0].endswith("pydoc"):
        LOGGING.info("Execution was not ended. Script name with 'pydoc' exception.")
        return

    try:
        with open(f"/proc/{os.getpid()}/cmdline", "r", encoding="utf-8") as f:
            content = f.read()

        if content.find("epydoc") != -1:
            LOGGING.info("Execution was not ended. Process content 'epydoc' exception.")
            return

        if content.find("sphinx") != -1:
            LOGGING.info("Execution was not ended. Process content 'sphinx' exception.")
            return

    except Exception as error:
        LOGGING.info(f"Exception caught, but the execution is ending anyway: '{error}'")


    LOGGING.info("".join((
        "Dogtail requires that Assistive Technology support to be enabled.",
        "You can enable accessibility with sniff or by running:",
        "'gsettings set org.gnome.desktop.interface toolkit-accessibility true'",
        "Aborting...",
    )))

    sys.exit(1)


def check_for_accessibility():
    """
    Checks if accessibility is enabled, and halts execution if it is not.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    if not is_accessibility_enabled():
        bail_because_accessibility_is_disabled()


def enable_accessibility(enable=True):
    """
    Enable Accessibility toolkit via dconf.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    from gi.repository.Gio import Settings

    a11y_dconf_key = "org.gnome.desktop.interface"
    try:
        interface_settings = Settings(schema_id=a11y_dconf_key)

    except TypeError:
        interface_settings = Settings(schema=a11y_dconf_key)

    interface_settings.set_boolean("toolkit-accessibility", enable)


def is_accessibility_enabled():
    """
    Checks if accessibility is enabled via DConf.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    from gi.repository.Gio import Settings

    a11y_dconf_key = "org.gnome.desktop.interface"
    try:
        interface_settings = Settings(schema_id=a11y_dconf_key)

    except TypeError:
        interface_settings = Settings(schema=a11y_dconf_key)
    dconf_enabled = interface_settings.get_boolean("toolkit-accessibility")

    if os.environ.get("GTK_MODULES", "").find("gail:atk-bridge") == -1:
        env_enabled = False

    else:
        env_enabled = True

    return dconf_enabled or env_enabled


def check_for_accessibility_interactively():
    """
    Checks if accessibility is enabled, and presents a dialog prompting the
    user if it should be enabled if it is not already, then halts execution.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    if is_a11y_enabled():
        LOGGING.debug("Accessibility already enabled.")
        return

    # Inspiration found in Gtk examples, lets not reinvent the wheel.
    class InteractiveDialog(Gtk.Dialog):
        """
        Interactive Dialog that user can confirm or cancel.
        """

        def __init__(self, parent):
            super().__init__(title="Are you sure?", transient_for=parent, flags=0)
            self.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
            )

            self.set_default_size(300, 100)
            self.set_resizable(False)

            grid = Gtk.Grid(column_spacing=10, row_spacing=10)

            # TODO is sniff still enough to just enable the toolkit?
            # Nowadays we need ponytail, xauthority to properly function on wayland.
            # using qecore-headless might be the only way to to properly enable everything.
            # In which case this function might be useless.
            question = """
            Dogtail requires Assistive Technology Support to be enabled for it to function.
            Would you like to enable Assistive Technology support now?

            Note that you might have to logout for the change to fully take effect.
            """

            label = Gtk.Label(label=question)
            grid.add(label)
            grid.set_margin_end(20)

            box = self.get_content_area()
            #box.add(label)

            box.add(grid)
            self.show_all()

    class InteractiveWindow(Gtk.Window):
        """
        Interactive window that will spawn question dialog.
        """

        def __init__(self):
            Gtk.Window.__init__(self, title="Interactive Check for Accessibility toolkit.")
            self.set_border_width(6)

            grid = Gtk.Grid(column_spacing=10, row_spacing=10)
            grid.set_margin_bottom(20)
            grid.set_margin_top(20)
            grid.set_margin_start(20)
            grid.set_margin_end(20)
            grid.set_column_homogeneous(True)
            grid.set_row_homogeneous(False)

            button = Gtk.Button(label="Enable toolkit-accessibility")
            button.connect("clicked", self.on_button_clicked)

            grid.add(button)

            self.add(grid)

        def on_button_clicked(self, widget): # pylint: disable=unused-argument
            """
            On click function.

            :param widget: Unused Gtk Button.
            :type widget: Gtk Button.
            """

            dialog = InteractiveDialog(self)
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                LOGGING.info("Enabling Accessibility.")
                enable_accessibility()
            elif response == Gtk.ResponseType.CANCEL:
                LOGGING.info("Execution halted, Accessibility Enabling was Cancelled.")
                bail_because_accessibility_is_disabled()

            # Destroy the dialog.
            dialog.destroy()
            # Destroy the main window.
            self.destroy()

    win = InteractiveWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


def wait_for_window(name, timeout=30):
    """
    Wait for window to appear. Currently wayland only.
    name can be a window 'title' as reported via Node.name
    or an app id (from .desktop file. i.e. "org.gnome.Calculator.desktop")
    Returns true on success, false on x11.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    from dogtail.rawinput import SESSION_TYPE
    from dogtail.ponytail_helper import ponytail_helper

    if SESSION_TYPE == "wayland":
        ponytail_interface = ponytail_helper.get_ponytail_interface()
        ponytail_interface.waitFor(name, timeout=timeout)
        return True

    return False


def get_current_x_window_position():
    """
    This is a helper to get window position (top left corner) solely by means of
    Xlib (direct X calls) - without a11y. This is targeted to be used with !GTK4!
    apps only - which don't support giving GLOBAL coords of their nodes under Xorg
    (as well as on wayland). By getting the win location and adding that up together
    with local coords, we can make actions with GTK4 apps under Xorg as well.
    Not to be mixed with what we do with local coords and local functions on W.

    Imports are used locally here not to bring unnecessary deps in most cases - because
    this is for rather a corner case... GTK4 apps will mostly be run in wayland and
    with Xorg most likely much much less.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    try:
        from Xlib import X, display
        from Xlib.error import XError
    except ModuleNotFoundError as error:
        raise ImportError("".join(
                (
                    "python-xlib is required for this script to run.",
                    "Please install it i.e. using 'pip3 install python-xlib'.",
                )
            )
        ) from error

    _display = display.Display()
    root = _display.screen().root

    prop = root.get_full_property(
        _display.intern_atom("_NET_ACTIVE_WINDOW"), X.AnyPropertyType
    )
    if prop is None:
        return 0, 0

    window_id = prop.value[0]

    window = _display.create_resource_object("window", window_id)

    try:
        geom = window.get_geometry()
        return geom.x, geom.y

    except XError as error:
        LOGGING.info(f"Error getting current window position: {error}")
        return (0, 0)


# Before cache
#'0.0014488697052001953' seconds - first call
#'0.0018050670623779297' seconds - all following calls

# After cache
#'0.0014488697052001953' seconds - first call
#'2.384185791015625e-06' seconds - all following calls

# Since 3.2
# Since 3.9 we could use @functools.cache
@functools.lru_cache
def get_screen_resolution():
    """
    Get resolution.

    :return: Resolution.
    :rtype: list
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    try:
        import dbus

        bus = dbus.SessionBus()
        obj = bus.get_object(
            "org.gnome.Mutter.DisplayConfig", "/org/gnome/Mutter/DisplayConfig"
        )
        interface = dbus.Interface(obj, "org.gnome.Mutter.DisplayConfig")
        call_method = interface.get_dbus_method("GetCurrentState")
        method_call_output = call_method()

        # Unwrapping the values to deal with usual types and not dbus types.
        def unwrap(value):
            if isinstance(value, dbus.ByteArray):
                return "".join([str(x) for x in value])
            if isinstance(value, (dbus.Array, list, tuple, dbus.Struct)):
                return [unwrap(x) for x in value]
            if isinstance(value, (dbus.Dictionary, dict)):
                return dict([(unwrap(x), unwrap(y)) for x, y in value.items()])
            if isinstance(value, (dbus.Signature, dbus.String)):
                return str(value)
            if isinstance(value, dbus.Boolean):
                return bool(value)
            if isinstance(
                value,
                (
                    dbus.Int16,
                    dbus.UInt16,
                    dbus.Int32,
                    dbus.UInt32,
                    dbus.Int64,
                    dbus.UInt64,
                ),
            ):
                return int(value)
            if isinstance(value, (dbus.Double)):
                return float(value)
            if isinstance(value, dbus.Byte):
                return bytes([int(value)])
            return value

        # Recursive helper function to walk the data structure.
        # Data structure is searched for current resolution.
        def search_dbus_structure(dbus_object, previous_object=None):

            # Check if the structure is dictionary.
            if isinstance(dbus_object, dict):
                for key, value in dbus_object.items():
                    # Check for the wanted condition of a dictionary.
                    # We need current display.
                    if key == "is-current" and value is True:
                        # If current object value is True
                        # return previous object's values.
                        return previous_object[1], previous_object[2]

                    # Check the result from the recursive function.
                    result_found = search_dbus_structure(value, dbus_object)
                    # End if there was result present. Return the value.
                    if result_found:
                        return result_found

            # Check if the structure is iterable but not a string.
            elif hasattr(dbus_object, "__iter__") and not isinstance(
                dbus_object, str
            ):
                # Check all the items present in the object.
                for item in dbus_object:
                    # Check the result from the recursive function.
                    result_found = search_dbus_structure(item, dbus_object)
                    # End if there was result present. Return the value.
                    if result_found:
                        return result_found

        resolution = search_dbus_structure(unwrap(method_call_output))
        LOGGING.debug(f"Resolution detected: '{resolution}'")
        return resolution
    except Exception as error:
        resolution = f"The resolution retrieval failed for: {error}"
        LOGGING.info(f"resolution error: '{resolution}'")
        return (0,0)


########################################
# Backwards compatibility definitions. #
########################################
def doDelay(delay=None):  # pylint: disable=invalid-name
    """
    Do Delay.
    """
    do_delay(delay=delay)


def waitForWindow(name, timeout=30): # pylint: disable=invalid-name
    """
    Wrapper over wait_for_window.
    """

    return wait_for_window(name=name, timeout=timeout)


def check_for_a11y_interactively():
    """
    Wrapper over check_for_accessibility_interactively.
    """

    return check_for_accessibility_interactively()


def checkForA11yInteractively(): # pylint: disable=invalid-name
    """
    Wrapper over check_for_a11y_interactively.
    """

    return check_for_accessibility_interactively()


def enable_a11y(enable=True):
    """
    Wrapper over enable_accessibility.
    """

    return enable_accessibility(enable=enable)


def enableA11y(enable=True): # pylint: disable=invalid-name
    """
    Wrapper over enable_accessibility.
    """

    return enable_accessibility(enable=enable)


def check_for_a11y():
    """
    Wrapper over check_for_accessibility.
    """

    return check_for_accessibility()


def checkForA11y(): # pylint: disable=invalid-name
    """
    Wrapper over check_for_accessibility.
    """

    return check_for_accessibility()


def is_a11y_enabled():
    """
    Wrapper over is_accessibility_enabled.
    """

    return is_accessibility_enabled()


def isA11yEnabled(): # pylint: disable=invalid-name
    """
    Wrapper over is_accessibility_enabled.
    """

    return is_accessibility_enabled()


def bail_because_a11y_is_disabled():
    """
    Wrapper over bail_because_accessibility_is_disabled.
    """

    return bail_because_accessibility_is_disabled()


def bailBecauseA11yIsDisabled(): # pylint: disable=invalid-name
    """
    Wrapper over bail_because_accessibility_is_disabled.
    """

    return bail_because_accessibility_is_disabled()


# TODO delete once all changes are applied.
# Keeping for now to not break something along the way.
class Highlight(Gtk.Window): # pylint: disable=missing-class-docstring
    def __init__(self):
        LOGGING.info("Deprecated on Wayland with release 2.0.")


class Blinker: # pylint: disable=missing-class-docstring
    def __init__(self):
        LOGGING.info("Deprecated on Wayland with release 2.0.")

###############################################
# End of backwards compatibility definitions. #
###############################################
