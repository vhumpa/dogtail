"""
Input injection over org.gnome.Mutter.RemoteDesktop, shaped like the ponytail
interface that rawinput.py already expects, without ScreenCast, PipeWire or
libei.
"""

import os  # noqa: I001 - require_version has to run between the two gi imports
import re
import subprocess
import warnings

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

# Mutter 50.2 and 50.3 eat the first three pointer events, six leaves headroom.
WARM_UP_EVENTS = int(os.environ.get("DOGTAIL_WARM_UP_EVENTS", "6"))

# Major versions the count above was measured against.
TESTED_MUTTER_MAJORS = (50,)


def _parse_mutter_version(text):
    """
    Pull a version out of the output of `mutter --version`.

    Recent versions say "mutter 50.3", older ones say "mutter 3.38.6".

    :param text: Output to parse.
    :type text: str

    :return: Major and minor version, or None if there is no version in there.
    :rtype: tuple(int, int) or None
    """

    match = re.search(r"mutter\s+(\d+)\.(\d+)", text)

    return (int(match.group(1)), int(match.group(2))) if match else None


def check_mutter_version():
    """
    Warn when the warm-up count has never been measured against this mutter.

    WARM_UP_EVENTS is a fixed count with no handshake behind it, because mutter
    offers no readiness signal. Undercounting it does not raise, the first click
    of the session just vanishes.

    :return: Major and minor version of the installed mutter, or None if it
        could not be run or its output held no version.
    :rtype: tuple(int, int) or None
    """

    try:
        output = subprocess.check_output(
            ["mutter", "--version"], text=True, stderr=subprocess.STDOUT, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    version = _parse_mutter_version(output)
    if version is None or version[0] in TESTED_MUTTER_MAJORS:
        return version

    warnings.warn(
        f"mutter {version[0]}.{version[1]} has not been tested with dogtail's "
        f"hermetic input warm-up (measured on {TESTED_MUTTER_MAJORS[0]}.x). "
        f"mutter drops pointer events while its virtual devices come up and "
        f"says nothing when it does, so if the first click of a session goes "
        f"missing, raise $DOGTAIL_WARM_UP_EVENTS above {WARM_UP_EVENTS}."
    )

    return version


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
        if some mutter drops more. The test_real_pointer_input test is the
        canary and $DOGTAIL_WARM_UP_EVENTS is the way out.
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
            return None  # noqa: RET501, PLR1711 - see the comment above

        ponytail_helper.get_window_id = get_window_id

    return backend


class _RecordingSession:
    """
    Stands in for the RemoteDesktop session proxy and records what got sent.
    """

    def __init__(self):
        self.calls = []

    def call_sync(self, method, arguments, *_rest):
        """
        Record a call instead of putting it on the bus.
        """

        self.calls.append((method, arguments.unpack() if arguments is not None else None))

    def motions(self):
        """
        Report the pointer motions recorded so far.

        :return: The deltas that were sent.
        :rtype: list(tuple(float, float))
        """

        return [arguments for method, arguments in self.calls
                if method == "NotifyPointerMotionRelative"]


class _Node:
    """
    Enough of a tree.Node for _guard_coordinates.
    """

    def __init__(self, extents, parent=None):
        self.extents = extents
        self.parent = parent
        self.name = "click me"
        self.roleName = "push button"  # pylint: disable=invalid-name


def demo():
    """
    Check the two things that go wrong quietly, without needing mutter.

    The relative-motion bookkeeping and the coordinate guard. Real end-to-end
    coverage is in tests/test_hermetic_gtk3.py.
    """

    from dogtail.hermetic.session import CoordinatesUnavailable

    backend = MutterInputBackend.__new__(MutterInputBackend)  # No bus needed.
    backend._session = _RecordingSession()
    backend._last_position = None

    # The first move anchors: slam into the corner, then go to (x, y).
    backend.generateMotionEvent(300, 200)
    assert backend._session.motions() == [(-100000.0, -100000.0), (300.0, 200.0)], \
        backend._session.motions()

    # Every move after is a plain delta. Re-slamming here is the corner paint bug.
    backend._session = _RecordingSession()
    backend.generateMotionEvent(310, 205)
    backend.generateMotionEvent(310, 205)
    assert backend._session.motions() == [(10.0, 5.0), (0.0, 0.0)], \
        backend._session.motions()

    # A new session has to anchor again.
    backend.disconnect()
    assert backend._last_position is None
    backend._session = _RecordingSession()
    backend.generateMotionEvent(40, 50)
    assert backend._session.motions()[0] == (-100000.0, -100000.0), \
        backend._session.motions()

    monitor = (1280, 1024)
    _guard_coordinates(_Node((0, 0, 1280, 1024)), monitor)  # Fullscreen, allowed.

    for extents in ((0, 0, 400, 200), (100, 100, 1280, 1024)):
        try:
            _guard_coordinates(_Node(extents), monitor)
            raise AssertionError(f"guard let {extents} through")
        except CoordinatesUnavailable as error:
            assert "window-local" in str(error), error

    # The guard checks the toplevel, not the widget you clicked.
    frame = _Node((0, 0, 400, 200))
    try:
        _guard_coordinates(_Node((10, 10, 80, 30), parent=frame), monitor)
        raise AssertionError("guard read the widget instead of its window")
    except CoordinatesUnavailable:
        pass

    assert _parse_mutter_version("mutter 50.3\n") == (50, 3)
    assert _parse_mutter_version("mutter 3.38.6\n") == (3, 38)
    assert _parse_mutter_version("bash: mutter: command not found") is None

    # An untested mutter has to warn rather than fail quietly.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        check_mutter_version()

    installed = _parse_mutter_version(
        subprocess.run(["mutter", "--version"], capture_output=True, text=True,
                       check=False).stdout
    )
    if installed is not None and installed[0] not in TESTED_MUTTER_MAJORS:
        assert caught, f"mutter {installed} is untested and nobody said so"
    else:
        assert not caught, [str(warning.message) for warning in caught]

    print("mutter.MutterInputBackend demo: OK")


if __name__ == "__main__":
    demo()
