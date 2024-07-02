#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
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

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from dogtail.logging import logging_class
LOGGING = logging_class.logger

from dogtail.config import config


def do_delay(delay=None):
    """
    Utility function to insert a delay (with logging and a configurable default delay).
    """

    if delay is None:
        delay = config.default_delay
        LOGGING.debug(f"Default Delay: Sleeping for '{delay}'")

    if config.debug_sleep:
        LOGGING.debug(f"Debug Sleep: Sleeping for '{delay}'")

    sleep(float(delay))


########################################
# Backwards compatibility definitions. #
########################################
def doDelay(delay=None):  # pylint: disable=invalid-name
    """
    Do Delay.
    """
    do_delay(delay=delay)
###############################################
# End of backwards compatibility definitions. #
###############################################


# TODO refactor this all.


# TODO if leaving it here, refactor it.
def run(
    string,
    timeout=30,#config.runTimeout,
    interval=0.5,#config.runInterval,
    desktop=None,
    dumb=False,
    appName="",
):
    """
    Runs an application.
    [For simple command execution such as 'rm *', use os.popen() or os.system()]
    If dumb is omitted or is False, polls at interval seconds until the application is finished
    starting, or until timeout is reached. If dumb is True, returns when timeout is reached.
    """

    #debug_log(
    #    "run(string=%s, timeout=%s, interval=%s, desktop=%s, dumb=%s, appName=%s)"
    #    % (
    #        str(string),
    #        str(timeout),
    #        str(interval),
    #        str(desktop),
    #        str(dumb),
    #        str(appName),
    #    )
    #)

    if not desktop:
        from dogtail.tree import root as desktop

    args = shlex.split(string)
    os.environ["GTK_MODULES"] = "gail:atk-bridge"
    pid = subprocess.Popen(args, env=os.environ).pid

    if not appName:
        appName = args[0]

    if dumb:
        #debug_log(
        #    "Disable startup detection. We're starting a non-AT-SPI-aware application."
        #)

        doDelay(timeout)

    else:
        #debug_log(
        #    "Startup detection code. The timing here is not totally precise, but it's good enough for now."
        #)

        time = 0

        while time < timeout:
            time = time + interval

            try:
                for child in desktop.children[::-1]:
                    if child.name == appName:
                        for grandchild in child.children:
                            if grandchild.roleName == "frame":
                                #from dogtail.procedural import focus
                                #focus.application.node = child
                                doDelay(interval)

                                return pid
            except AttributeError:  # pragma: no cover
                pass

            doDelay(interval)

    return pid






# For now commenting this out.
#class Highlight(Gtk.Window):  # pragma: no cover
#    """
#    Hightlight class used by Blinker. Display a red rectangle corresponding to the Accessibility
#    node position and size via Gtk.Window class.
#    """
#
#    def __init__(self, x, y, w, h):
#        super(Highlight, self).__init__()
#
#        self.x = x
#        self.y = y
#        self.w = w
#        self.h = h
#        self.set_decorated(False)
#        self.set_has_resize_grip(False)
#        self.maximize()
#        self.screen = self.get_screen()
#        self.visual = self.screen.get_rgba_visual()
#
#        if self.visual is not None and self.screen.is_composited():
#            self.set_visual(self.visual)
#
#        self.set_app_paintable(True)
#        self.connect("draw", self.area_draw)
#        self.show_all()
#
#    def area_draw(self, widget, cr):
#        """
#        Draw a rectangle on the screen.
#        """
#
#        debug_log("Drawing the node on the screen.")
#
#        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
#        cr.set_operator(cairo.OPERATOR_SOURCE)
#        cr.paint()
#        cr.set_operator(cairo.OPERATOR_OVER)
#        cr.set_source_rgb(0.9, 0.1, 0.1)
#        cr.set_line_width(6)
#        cr.rectangle(self.x, self.y, self.w, self.h)
#        cr.stroke()
#
#
#class Blinker:  # pragma: no cover
#    """
#    Blinker class used to highlight the Accessibility node in graphical interface.
#    This highlight will be seen for 1 second before it will disappear.
#    """
#
#    INTERVAL_MS = 1000
#
#    def __init__(self, x, y, w, h):
#        self.highlight_window = Highlight(x, y, w, h)
#        if self.highlight_window.screen.is_composited() is not False:
#            self.timeout_handler_id = GLib.timeout_add(
#                Blinker.INTERVAL_MS, self.destroyHighlight
#            )
#            Gtk.main()
#        else:
#            self.highlight_window.destroy()
#
#    def destroyHighlight(self):
#        """
#        Remove the highlight.
#        """
#
#        debug_log("Blinker destroy highlight.")
#
#        self.highlight_window.destroy()
#        Gtk.main_quit()
#
#        return False


class Lock(object):
    """
    A known sytem-wide mutex implementation that uses atomicity of the mkdir operation in UNIX-like
    systems. This should be used mainly to provide mutual exclution in handling possible collisions
    among multiple script instances. You can choose to make randomized single-script wise locks
    or a more general locks if you do not choose to randomize the lockdir name. Set unLockOnExit
    to True to enable automatic unlock when scipt process exits to avoid having to unlock manually.
    """

    def __init__(
        self,
        location="/tmp",
        lockname="dogtail_lockdir_",
        randomize=True,
        unlockOnExit=False,
    ):
        """
        You can change the default lockdir location or name. Setting randomize to
        False will result in no random string being appened to the lockdir name.
        """

        self.lockdir = os.path.join(os.path.normpath(location), lockname)
        if randomize:
            self.lockdir = "".join((self.lockdir, self.__getPostfix()))

        self.unlockOnExit = unlockOnExit

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

        #debug_log(
        #    "Create a lock directory. Raising the exception if the lock is already present."
        #)

        locked_msg = "Dogtail lock: Already locked with the same lock."

        if not os.path.exists(self.lockdir):
            try:
                os.mkdir(self.lockdir)
            except OSError as error:
                if error.errno == errno.EEXIST and os.path.isdir(self.lockdir):
                    raise OSError(locked_msg)

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

        #debug_log("Remove the lock. Raising the exception if the lock is not present.")

        # if self.unlockOnExit:
        #    raise Exception('Cannot unlock with unlockOnExit set to True!')

        if os.path.exists(self.lockdir):
            try:
                os.rmdir(self.lockdir)
            except OSError as error:
                if error.errno == errno.EEXIST:
                    raise OSError("Dogtail unlock: lockdir removed elsewhere!")
        else:
            raise OSError("Dogtail unlock: not locked")

    def locked(self):
        """
        Check if locked directory exists.
        """

        #debug_log("Checking if locked directory exists.")

        return os.path.exists(self.lockdir)

    def __getPostfix(self):
        """
        Generate a length of 5 random string that serves as file name suffix.
        """

        import random
        import string

        #debug_log("Get random file suffix of length 5.")

        return "".join(
            random.choice(string.ascii_letters + string.digits) for x in range(5)
        )


a11yDConfKey = "org.gnome.desktop.interface"


def isA11yEnabled():
    """
    Checks if accessibility is enabled via DConf.
    """

    #debug_log("isA11yEnabled()")

    from gi.repository.Gio import Settings

    try:
        InterfaceSettings = Settings(schema_id=a11yDConfKey)
    except TypeError:
        InterfaceSettings = Settings(schema=a11yDConfKey)

    dconfEnabled = InterfaceSettings.get_boolean("toolkit-accessibility")

    if os.environ.get("GTK_MODULES", "").find("gail:atk-bridge") == -1:
        envEnabled = False
    else:
        envEnabled = True  # pragma: no cover

    return dconfEnabled or envEnabled


def bailBecauseA11yIsDisabled():
    """
    Accessibility is detected as enabled. End the execution if there are no exceptions.
    """

    #debug_log("bailBecauseA11yIsDisabled()")

    if sys.argv[0].endswith("pydoc"):
        #debug_log("Execution was not ended. Script name with 'pydoc' exception.")
        return

    try:
        with open("/proc/%s/cmdline" % os.getpid(), "r") as f:
            content = f.read()

        if content.find("epydoc") != -1:
            #debug_log("Execution was not ended. Proces content 'epydoc' exception.")
            return  # pragma: no cover
        if content.find("sphinx") != -1:
            #debug_log("Execution was not ended. Proces content 'sphinx' exception.")
            return  # pragma: no cover
    except Exception:  # pragma: no cover
        pass

    #logger.log(
    #    "\n".join(
    #        (
    #            "Dogtail requires that Assistive Technology support be enabled.",
    #            "You can enable accessibility with sniff or by running:",
    #            "'gsettings set org.gnome.desktop.interface toolkit-accessibility true'",
    #            "Aborting...",
    #        )
    #    )
    #)

    sys.exit(1)


def enableA11y(enable=True):
    """
    Enables accessibility via DConf.
    """

    #debug_log("enableA11y(enable=%s)" % str(enable))

    from gi.repository.Gio import Settings

    InterfaceSettings = Settings(schema_id=a11yDConfKey)
    InterfaceSettings.set_boolean("toolkit-accessibility", enable)


def checkForA11y():  # pragma: no cover
    """
    Checks if accessibility is enabled, and halts execution if it is not.
    """

    #debug_log("checkForA11y()")

    if not isA11yEnabled():
        bailBecauseA11yIsDisabled()


def checkForA11yInteractively():  # pragma: no cover
    """
    Checks if accessibility is enabled, and presents a dialog prompting the
    user if it should be enabled if it is not already, then halts execution.
    """

    #debug_log("checkForA11yInteractively()")

    if isA11yEnabled():
        return

    #dialog = Gtk.Dialog(
    #    "Enable Assistive Technology Support?",
    #    None,
    #    Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
    #    (Gtk.STOCK_QUIT, Gtk.ResponseType.CLOSE, "_Enable", Gtk.ResponseType.ACCEPT),
    #)

    #question = """
    #    Dogtail requires that Assistive Technology Support be enabled for it to function. Would you like to
    #    enable Assistive Technology support now?
#
    #    Note that you will have to log out for the change to fully take effect.
    #""".strip()

    pass
    #dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    #questionLabel = Gtk.Label(label=question)
    #questionLabel.set_line_wrap(True)
    #dialog.vbox.pack_start(questionLabel, True, True, 0)
    #dialog.show_all()
    #result = dialog.run()
#
    #if result == Gtk.ResponseType.ACCEPT:
    #    logger.log("Enabling accessibility...")
    #    enableA11y()
    #elif result == Gtk.ResponseType.CLOSE:
    #    bailBecauseA11yIsDisabled()
    #dialog.destroy()


def waitForWindow(name, timeout=30):
    """
    Wait for window to appear. Currently wayland only.
    name can be a window 'title' as reported via Node.name
    or an app id (from .desktop file. i.e. "org.gnome.Calculator.desktop")
    Returns true on success, false on x11.
    """

    #debug_log("waitForWindow(name=%s, timeout=%s)" % (name, str(timeout)))

    #from dogtail.rawinput import ponytail, SESSION_TYPE
#
    #if SESSION_TYPE == "wayland":
    #    ponytail.waitFor(name, timeout=timeout)
    #    return True
    #else:
    #    return False
    return True


def get_current_x_window_position():
    """
    This is a helper to get window possition (top left corner) solely by means of
    Xlib (direct X calls) - without a11y. This is targeted to be used with !GTK4!
    apps only - which don't support giving GLOBAL coords of their nodes under Xorg
    (as well as on wayland). By getting the win location and adding that up together
    with local coords, we can make actions with GTK4 apps under Xorg as well.
    Not to be mixed with what we do with local coords and local functions on W.

    Imports are used locally here not to bring uncessery deps in most cases - because
    this is for rather a corner case... GTK4 apps will mostly be run in wayland and
    with Xorg most likely much much less.
    """

    try:
        from Xlib import X, display
        from Xlib.error import XError
    except ModuleNotFoundError as e:
        raise ImportError(
            "python-xlib is required for this script to run. Please install it i.e. using 'pip install python-xlib'."
        ) from e

    d = display.Display()
    root = d.screen().root
    window_id = root.get_full_property(
        d.intern_atom("_NET_ACTIVE_WINDOW"), X.AnyPropertyType
    ).value[0]
    window = d.create_resource_object("window", window_id)

    try:
        geom = window.get_geometry()
        return geom.x, geom.y
    except XError as e:
        print(f"Error getting current window position: {e}")
        return 0, 0


def get_screen_resolution():
    """Additional helper function with similar reasoning as the get_current_x_window_position needed
    to work with GTK4 apps - even on wayland! (needs Xwayland running for xlib to get this info).
    We need this to detect whether the frame is in fullscreen mode in order to either use the config.gtk4Offset
    or not. There is no offset when window is full-screen. Se README for more info on this and shadows.
    """
    try:
        from Xlib import X, display
        from Xlib.error import XError
    except ModuleNotFoundError as e:
        raise ImportError(
            "python-xlib is required for this script to run. Please install it i.e. using 'pip install python-xlib'."
        ) from e

    d = display.Display()
    screen = d.screen()
    width = screen.width_in_pixels
    height = screen.height_in_pixels
    return width, height
