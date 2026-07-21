"""
Input injection over org.gnome.Mutter.RemoteDesktop, shaped like the ponytail
interface that rawinput.py already expects. No ScreenCast, no PipeWire, no libei.
"""

import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib


BUS_NAME = "org.gnome.Mutter.RemoteDesktop"
OBJECT_PATH = "/org/gnome/Mutter/RemoteDesktop"
INTERFACE = "org.gnome.Mutter.RemoteDesktop"
SESSION_INTERFACE = "org.gnome.Mutter.RemoteDesktop.Session"

# Dogtail passes X11 button numbers, mutter wants evdev ones.
BUTTON_MAP = {1: 272, 2: 274, 3: 273}

KEYSYM_SHIFT_L = 0xFFE1

# Mutter 50.2 eats the first three pointer events, six leaves headroom.
WARM_UP_EVENTS = 6


class MutterInputBackend:
    """
    Injects input over RemoteDesktop, standing in for the ponytail interface.

    The public methods here are camelCase on purpose. They duck-type whatever
    PonytailHelper.get_ponytail_interface() hands back, and rawinput.py calls
    them by those names.
    """

    def __init__(self, bus_address=None):
        """
        Connect to RemoteDesktop. No session is created until input is sent.

        :param bus_address: Private bus to connect to, defaults to the session bus
        :type bus_address: str, optional
        """

        self._bus = Gio.DBusConnection.new_for_address_sync(
            bus_address, Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT
                       | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
            None, None,
        ) if bus_address else Gio.bus_get_sync(Gio.BusType.SESSION, None)

        self._manager = Gio.DBusProxy.new_sync(
            self._bus, Gio.DBusProxyFlags.NONE, None,
            BUS_NAME, OBJECT_PATH, INTERFACE, None,
        )

        self._session_path = None
        self._session = None
        self.connected = None
        self.window_list = []  # Needs Shell.Introspect, which we do not have.
        self._last_position = None

    # -- session lifecycle -------------------------------------------------

    def _ensure_session(self):
        """
        Create and start a RemoteDesktop session, once.
        """

        if self._session is not None:
            return

        result = self._manager.call_sync(
            "CreateSession", None, Gio.DBusCallFlags.NONE, -1, None,
        )
        (self._session_path,) = result.unpack()
        self._session = Gio.DBusProxy.new_sync(
            self._bus, Gio.DBusProxyFlags.NONE, None,
            BUS_NAME, self._session_path, SESSION_INTERFACE, None,
        )
        self._session.call_sync("Start", None, Gio.DBusCallFlags.NONE, -1, None)
        self._warm_up()

    def _warm_up(self):
        """
        Burn the events mutter drops while its virtual devices come up.

        Start() returns before the devices are ready and the dropped events
        raise nothing. Both throwaways are no-ops: motion of (0, 0) gets
        overridden by the next move, a lone Shift_L changes nothing.

        The count is fixed rather than a handshake, so it undercounts silently
        if some mutter drops more. The test_real_pointer_input test is the canary.
        """

        for _ in range(WARM_UP_EVENTS):
            self._notify_motion_relative(0.0, 0.0)

        self.generateKeysymEvent(KEYSYM_SHIFT_L)

    def _notify_motion_relative(self, delta_x, delta_y):
        """
        Move the pointer by a delta.

        :param delta_x: Horizontal movement in pixels.
        :type delta_x: float

        :param delta_y: Vertical movement in pixels.
        :type delta_y: float
        """

        self._session.call_sync(
            "NotifyPointerMotionRelative",
            GLib.Variant("(dd)", (delta_x, delta_y)),
            Gio.DBusCallFlags.NONE, -1, None,
        )

    def connectMonitor(self, *_args, **_kwargs):
        """
        Connect to the monitor, in the sense rawinput.py means it.
        """

        self._ensure_session()
        self.connected = "monitor"

    def connectWindow(self, window_id):
        """
        Connect to a window, which without Introspect is the monitor again.

        Separate from connectMonitor only because rawinput.py calls both.

        :param window_id: Window rawinput.py wants to talk to.
        :type window_id: str
        """

        self._ensure_session()
        self.connected = window_id

    def disconnect(self):
        """
        Stop the RemoteDesktop session and forget where the pointer was.
        """

        if self._session is not None:
            try:
                self._session.call_sync("Stop", None, Gio.DBusCallFlags.NONE, -1, None)
            except GLib.Error:
                pass

        self._session = None
        self._session_path = None
        self.connected = None
        self._last_position = None

    # -- pointer -----------------------------------------------------------

    def generateMotionEvent(self, x, y):
        """
        Move the pointer to absolute screen coordinates.

        Absolute motion needs a ScreenCast stream, and so PipeWire, so this
        fakes it: slam into the top-left corner, which clamps to (0, 0), then
        move relative from there. Only the first move of a session needs the
        slam. Doing it again mid-drag would paint a stroke through the corner.

        :param x: Target horizontal coordinate.
        :type x: int

        :param y: Target vertical coordinate.
        :type y: int
        """

        self._ensure_session()

        if self._last_position is None:
            self._notify_motion_relative(-100000.0, -100000.0)
            self._notify_motion_relative(float(x), float(y))
        else:
            last_x, last_y = self._last_position
            self._notify_motion_relative(float(x) - last_x, float(y) - last_y)

        self._last_position = (x, y)

    def generateButtonPress(self, button):
        """
        Press a pointer button.

        :param button: X11 button number.
        :type button: int
        """

        self._ensure_session()
        self._session.call_sync(
            "NotifyPointerButton",
            GLib.Variant("(ib)", (BUTTON_MAP.get(button, button), True)),
            Gio.DBusCallFlags.NONE, -1, None,
        )

    def generateButtonRelease(self, button):
        """
        Release a pointer button.

        :param button: X11 button number.
        :type button: int
        """

        self._ensure_session()
        self._session.call_sync(
            "NotifyPointerButton",
            GLib.Variant("(ib)", (BUTTON_MAP.get(button, button), False)),
            Gio.DBusCallFlags.NONE, -1, None,
        )

    def generateButtonEvent(self, button, x, y):
        """
        Move to a point and click there.

        :param button: X11 button number.
        :type button: int

        :param x: Target horizontal coordinate.
        :type x: int

        :param y: Target vertical coordinate.
        :type y: int
        """

        self.generateMotionEvent(x, y)
        self.generateButtonPress(button)
        self.generateButtonRelease(button)

    # -- keyboard ----------------------------------------------------------
    # Dogtail hands us X keycodes, evdev plus 8 by the XKB convention, and
    # mutter wants raw evdev, hence the -8 below.

    def generateKeycodePress(self, key_code):
        """
        Press a key by keycode.

        :param key_code: X keycode.
        :type key_code: int
        """

        self._ensure_session()
        self._session.call_sync(
            "NotifyKeyboardKeycode",
            GLib.Variant("(ub)", (key_code - 8, True)),
            Gio.DBusCallFlags.NONE, -1, None,
        )

    def generateKeycodeRelease(self, key_code):
        """
        Release a key by keycode.

        :param key_code: X keycode.
        :type key_code: int
        """

        self._ensure_session()
        self._session.call_sync(
            "NotifyKeyboardKeycode",
            GLib.Variant("(ub)", (key_code - 8, False)),
            Gio.DBusCallFlags.NONE, -1, None,
        )

    def generateKeycodeEvent(self, key_code):
        """
        Press and release a key by keycode.

        :param key_code: X keycode.
        :type key_code: int
        """

        self.generateKeycodePress(key_code)
        self.generateKeycodeRelease(key_code)

    def generateKeysymEvent(self, key_symbol_value, delay=None):
        """
        Press and release a key by keysym.

        :param key_symbol_value: X keysym.
        :type key_symbol_value: int

        :param delay: Accepted for interface compatibility and unused, defaults to None
        :type delay: float, optional
        """

        self._ensure_session()
        for pressed in (True, False):
            self._session.call_sync(
                "NotifyKeyboardKeysym",
                GLib.Variant("(ub)", (key_symbol_value, pressed)),
                Gio.DBusCallFlags.NONE, -1, None,
            )


def _toplevel_of(node):
    """
    Walk up to the window a node lives in.

    :param node: Node to start from.
    :type node: dogtail.tree.Node

    :return: The topmost node below the application.
    :rtype: dogtail.tree.Node
    """

    toplevel = node
    while toplevel.parent is not None and toplevel.parent.roleName != "application":
        toplevel = toplevel.parent

    return toplevel


def _guard_coordinates(node, monitor_size):
    """
    Refuse a click that would land somewhere other than where the caller thinks.

    A wayland client is never told where it got placed, so at-spi reports every
    window at (0, 0) and its widgets relative to that, while injection is
    screen-global. The two only line up when the window fills the monitor.

    :param node: Node that is about to be clicked.
    :type node: dogtail.tree.Node

    :param monitor_size: Width and height of the virtual monitor.
    :type monitor_size: tuple(int, int)

    :raises CoordinatesUnavailable: The window does not fill the monitor.
    """

    from dogtail.hermetic.session import CoordinatesUnavailable

    toplevel = _toplevel_of(node)
    size = toplevel.extents[2:]
    if toplevel.extents[:2] == (0, 0) and size == tuple(monitor_size):
        return

    raise CoordinatesUnavailable(
        f"{node.name or node.roleName!r} sits in a {size[0]}x{size[1]} window, "
        f"the monitor is {monitor_size[0]}x{monitor_size[1]}. at-spi coords are "
        f"window-local on wayland and injection is screen-global, so this click "
        f"would land somewhere else entirely. use doActionNamed(), or fullscreen "
        f"the window first with session.fullscreen(app)."
    )


def install(bus_address=None, monitor_size=None):
    """
    Swap this backend in as the ponytail interface.

    There is no backend seam in dogtail, but everything goes through the
    PonytailHelper singleton, so patching that beats touching the dozen-odd
    inline branches in rawinput.py.

    Pass monitor_size to arm the coordinate guard. It hangs off get_window_id
    because that is the one place on the click path still holding the node. A
    bare rawinput.click(x, y) skips it, and has nothing to check anyway.

    :param bus_address: Private bus to connect to, defaults to the session bus
    :type bus_address: str, optional

    :param monitor_size: Width and height of the virtual monitor, defaults to
        None, which leaves the coordinate guard disarmed
    :type monitor_size: tuple(int, int), optional

    :return: The installed backend.
    :rtype: MutterInputBackend
    """

    from dogtail.ponytail_helper import ponytail_helper

    backend = MutterInputBackend(bus_address=bus_address)
    ponytail_helper._ponytail_dbus_interface = backend
    ponytail_helper._already_initiated = True

    if monitor_size is not None:
        def get_window_id(accessible_object):
            _guard_coordinates(accessible_object, monitor_size)

            # None, not "". An empty string skips the disconnect and settle
            # that ponytail_check_connection does for None, and that settle
            # time turned out to matter.
            return None

        ponytail_helper.get_window_id = get_window_id

    return backend


def demo():
    """
    Say where the real coverage is.

    RemoteDesktop only exists once mutter is up, so there is nothing to check
    standalone. The tests/test_hermetic_gtk3.py module drives this for real.
    """

    print("mutter.MutterInputBackend: see tests/test_hermetic_gtk3.py")


if __name__ == "__main__":
    demo()
