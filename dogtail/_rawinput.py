#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release. raw input.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# ruff: noqa: E402
# ruff: noqa: E501


from __future__ import absolute_import, division, print_function, unicode_literals

import os

import gi

gi.require_version("Atspi", "2.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk
from gi.repository import Atspi

import warnings
warnings.filterwarnings("ignore", "g_object_unref")

from .utils import do_delay

from _ponytail_connection import PonytailWrapper, ponytail_check_connection

# TODO To be change to dogtail.logging before release.
from _logging import Logging
logging_class = Logging()
LOGGER = logging_class.logger


from .config import read_config
configuration = read_config()


SESSION_TYPE = "x11"
if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
    os.system("gsettings set org.gnome.shell introspect true")
    SESSION_TYPE = "wayland"


# There is a better way to do this since I am already rewriting it.
def update_coords(coords):
    """
    Lets fo this better that this.
    """

    # Reserved for wrong coordinates reporting.
    return coords


# Coordinate check for a negative value.
def check_coordinates(x, y):
    """
    Simple coordination check for positive coordinates.
    """

    message = f"Attempting to generate a mouse event at negative coordinates: ({x},{y})"

    # Lets not check against 0.
    # There are shadows in effect that can go beyond the screen.
    # Its not unusual for coordinate to be around -10 to -30.
    if x < -50 or y < -50:
        raise ValueError(message)


def do_typing_delay():
    """
    Execute a typing delay.
    """
    do_delay(configuration["typing_delay"])


def click(x, y, button=1, check=True, window_id=None):
    """
    Synthesize a mouse button click at coordinates (x, y).
    """

    # Get ponytail only when required.
    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    # TODO, remove and do it better.
    (_x, _y) = update_coords((x, y))

    # Check if the coordinates are not
    if check:
        check_coordinates(_x, _y)

    LOGGER.debug(f"Mouse button '{button}' click at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name=f"b{button}c")
    else:
        ponytail_check_connection(window_id)
        ponytail.generateButtonEvent(button, _x, _y)

    do_delay(configuration["default_delay"])


def point(x, y, check=True, window_id=None):
    """
    Synthesize a button point at (x,y)
    """

    # Get ponytail only when required.
    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    # TODO, remove and do it better.
    (_x, _y) = update_coords((x, y))

    # Check if the coordinates are not
    if check:
        check_coordinates(_x, _y)

    LOGGER.debug(f"Mouse over at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name="abs")
    else:
        ponytail_check_connection(window_id)
        ponytail.generateMotionEvent(_x, _y)

    do_delay(configuration["default_delay"])


def double_click(x, y, button=1, check=True, window_id=None):
    """
    Synthesize a mouse button double-click at (x,y)
    """

    # Get ponytail only when required.
    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    # TODO, remove and do it better.
    (_x, _y) = update_coords((x, y))

    # Check if the coordinates are not
    if check:
        check_coordinates(x, y)

    LOGGER.debug(f"Mouse button '{button}' double-click at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(x, y, name=f"b{button}d")
    else:
        ponytail_check_connection(window_id)
        ponytail.generateButtonEvent(button, _x, _y)

        do_delay(configuration["double_click_delay"])

        # Prevent executing release event on closed application
        ponytail.generateButtonPress(button)
        if ponytail.connected:
            ponytail.generateButtonRelease(button)
        else: # not ponytail.connected:
            ponytail.connectMonitor()
            ponytail.generateButtonRelease(button)

    do_delay(configuration["default_delay"])


def press(x, y, button=1, check=True, window_id=None, delay=None):
    """
    Synthesize a mouse button press at (x,y)
    """

    # Check if user defined their own delay.
    if delay:
        delay_to_use = delay
    else:
        delay_to_use = configuration["default_delay"]

    # Get ponytail only when required.
    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    (_x, _y) = update_coords((x, y))

    if check:
        check_coordinates(_x, _y)

    LOGGER.debug(f"Mouse button '{button}' press at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name=f"b{button}p")

    else:
        ponytail_check_connection(window_id)
        ponytail.generateMotionEvent(_x, _y)
        ponytail.generateButtonPress(button)

    do_delay(delay_to_use)


def release(x, y, button=1, check=True, window_id=None):
    """
    Synthesize a mouse button release at (x,y)
    """

    # Get ponytail only when required.
    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    (_x, _y) = update_coords((x, y))

    if check:
        check_coordinates(_x, _y)

    LOGGER.debug(f"Mouse button '{button}' release at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name=f"b{button}r")

    else:
        ponytail_check_connection(window_id)
        ponytail.generateMotionEvent(_x, _y)

        do_delay()

        ponytail.generateButtonRelease(button)

    do_delay()


def absolute_motion(x, y, mouse_delay=None, check=True, window_id=None):
    """
    Synthesize mouse absolute motion to (x,y)
    """

    # Get ponytail only when required.
    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    # Check if user defined their own delay.
    if mouse_delay:
        delay_to_use = mouse_delay
    else:
        delay_to_use = configuration["default_delay"]

    (_x, _y) = update_coords((x, y))

    if check:
        check_coordinates(_x, _y)

    LOGGER.debug(f"Mouse absolute motion at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name="abs")

    else:
        ponytail_check_connection(window_id)
        ponytail.generateMotionEvent(_x, _y)

    do_delay(delay_to_use)


def absolute_motion_with_trajectory(
        source_x,
        source_y,
        destination_x,
        destination_y,
        mouse_delay=None,
        check=True,
        window_id=None
    ):
    """
    Synthesize mouse absolute motion with trajectory.
    The 'trajectory' means that the whole motion is divided into several atomic
    movements which are Synthesize separately.
    """

    # Get ponytail only when required.
    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    # Check if user defined their own delay.
    if mouse_delay:
        delay_to_use = mouse_delay
    else:
        delay_to_use = configuration["default_delay"]

    if check:
        check_coordinates(source_x, source_y)
        check_coordinates(destination_x, destination_y)

    LOGGER.debug(f"Mouse absolute motion with trajectory at ({destination_x}, {destination_y})")

    if SESSION_TYPE == "wayland":
        ponytail_check_connection(window_id)

    difference_x = float(destination_x - source_x)
    difference_y = float(destination_y - source_y)
    max_length = max(abs(difference_x), abs(difference_y))

    if max_length == 0:
        return

    difference_x = difference_x / max_length
    difference_y = difference_y / max_length
    act_x = float(source_x)
    act_y = float(source_y)

    for _ in range(0, int(max_length)):
        act_x += difference_x
        act_y += difference_y

        if mouse_delay:
            do_delay(mouse_delay)

        if SESSION_TYPE == "x11":
            # TODO Newton if condition.
            Atspi.generate_mouse_event(int(act_x), int(act_y), name="abs")

        else:
            ponytail.generateMotionEvent(int(act_x), int(act_y))

    do_delay(delay_to_use)


def relative_motion(x, y, mouse_delay=None):
    """
    Synthesize a relative motion from actual position.
    Note: Does not check if the end coordinates are positive.
    """

    LOGGER.debug(f"Mouse relative motion of ({x}, {y})")

    if SESSION_TYPE == "wayland":
        LOGGER.debug("Relative motion unavailable under wayland not available.")
        return

    # TODO Newton if condition.
    Atspi.generate_mouse_event(x, y, name="rel")

    if mouse_delay:
        do_delay(mouse_delay)
    else:
        do_delay()


def drag(fromXY, toXY, button=1, check=True):  # pylint: disable=invalid-name
    """
    Synthesize a mouse press, drag, and release on the screen.
    """

    LOGGER.debug(f"Mouse button '{button}' drag from '{fromXY}' to '{toXY}'")

    (_x, _y) = fromXY
    press(x=_x, y=_y, button=button, check=check)

    (_x, _y) = toXY
    absolute_motion(x=_x, y=_y, check=check)
    do_delay()

    release(x=_x, y=_y, button=button, check=check)
    do_delay()


def drag_node_to_node(source_node, destination_node, button=1, check=True):
    """
    Drag source_node onto dest_node. These are tree.Node objects. Takes positions
    of these Nodes directly, so you don't have to calculate end enter them directly.
    """

    LOGGER.debug(f"Dragging from '{str(source_node)}' to '{str(destination_node)}'.")
    LOGGER.debug(f"Dragging using button '{button}' and check '{check}'")

    x = int(source_node.position[0] + source_node.size[0] / 2)
    y = int(source_node.position[1] + source_node.size[1] / 2)
    press(x, y, button, check, source_node.window_id)

    x = int(destination_node.position[0] + destination_node.size[0] / 2)
    y = int(destination_node.position[1] + destination_node.size[1] / 2)

    release(x, y, button, check, window_id=destination_node.window_id)
    do_delay()


def drag_with_trajectory(  # pylint: disable=invalid-name
        fromXY,
        toXY,
        button=1,
        check=True,
        press_delay=0.5,
        mouse_delay=0.01
    ):
    """
    Synthesize a mouse press, drag (including move events), and release on the screen
    Please note, that on Wayland, this function works for drags only within a single window.
    On X this function works with global coords and equals dragWithTrajectoryGlobal
    """

    # Check if user defined their own delay.
    if press_delay:
        delay_to_use = press_delay
    else:
        delay_to_use = configuration["default_delay"]

    LOGGER.debug(f"Dragging with trajectory from '{fromXY}' to '{toXY}'.")
    LOGGER.debug(f"Dragging using button '{button}' and check '{check}'")
    LOGGER.debug(f"Dragging using press delay '{delay_to_use}' and mouse_delay '{mouse_delay}'")

    (from_x, from_y) = fromXY
    press(x=from_x, y=from_y, button=button, check=check, delay=delay_to_use)

    (to_x, to_y) = toXY
    absolute_motion_with_trajectory(
        source_x=fromXY[0],
        source_y=fromXY[1],
        destination_x=to_x,
        destination_y=to_y,
        mouse_delay=mouse_delay,
        check=check
    )
    do_delay()

    release(x=to_x, y=to_y, button=button, check=check)
    do_delay()


def drag_with_trajectory_global(fromXY, toXY, button=1):  # pylint: disable=invalid-name
    """
    Synthesize a mouse press, drag (including move events), and release on the screen
    For use on Wayland - as this function forces using global coords, although we get
    local ones from a11y. So this function is targeted to be used for inter-window drags
    on Wayland, where you will need to quesstimate the coords. Which is doable i.e by
    having source window placed on the left *half* of the screen (local coords will be
    very similar to globals perhaps with the top panel offset).

    Having 'trajectory' appears to be necessary on Wayland for any drags.
    Use 'drag_with_trajectory' or just 'drag' on X sessions like in pre-wayland
    version of dogtail.
    """

    # Get ponytail only when required.
    ponytail_wrapper = PonytailWrapper()
    ponytail = ponytail_wrapper.get_ponytail_instance()

    LOGGER.debug(f"Dragging with trajectory from '{fromXY}' to '{toXY}', button '{button}'.")

    if SESSION_TYPE == "wayland":
        (x, y) = fromXY
        ponytail_check_connection(window_id="")

        ponytail.generateMotionEvent(x, y)
        do_delay(configuration["default_delay"])

        ponytail.generateButtonPress(1)
        do_delay(configuration["default_delay"])

        (x, y) = toXY
        absoluteMotionWithTrajectory(fromXY[0], fromXY[1], x, y, mouseDelay=0.01, window_id="")

        ponytail.generateMotionEvent(x, y)
        do_delay(configuration["default_delay"])

        ponytail.generateButtonRelease(1)
        do_delay()

    else:
        drag_with_trajectory(fromXY, toXY, button)


########################################
# Backwards compatibility definitions. #
########################################
def doubleClick(x, y, button=1, check=True, window_id=None):  # pylint: disable=invalid-name
    """
    Synthesize a mouse button double-click at (x,y)
    """

    double_click(x=x, y=y, button=button, check=check, window_id=window_id)


def doTypingDelay():  # pylint: disable=invalid-name
    """
    Execute a typing delay.
    """

    do_typing_delay()


def absoluteMotion(x, y, mouseDelay=None, check=True, window_id=None):  # pylint: disable=invalid-name
    """
    Synthesize mouse absolute motion to (x,y)
    """

    absolute_motion(x=x, y=y, mouse_delay=mouseDelay, check=check, window_id=window_id)


def absoluteMotionWithTrajectory(  # pylint: disable=invalid-name
        source_x,
        source_y,
        dest_x,
        dest_y,
        mouseDelay=None,
        check=True,
        window_id=None
    ):
    """
    Synthesize mouse absolute motion with trajectory.
    The 'trajectory' means that the whole motion is divided into several atomic
    movements which are Synthesize separately.
    """

    absolute_motion_with_trajectory(
        source_x=source_x,
        source_y=source_y,
        destination_x=dest_x,
        destination_y=dest_y,
        mouse_delay=mouseDelay,
        check=check,
        window_id=window_id
    )


def relativeMotion(x, y, mouseDelay=None):  # pylint: disable=invalid-name
    """
    Synthesize a relative motion from actual position.
    Note: Does not check if the end coordinates are positive.
    """

    relative_motion(x=x, y=y, mouse_delay=mouseDelay)


def dragNodeToNode(source_node, dest_node, button=1, check=True):  # pylint: disable=invalid-name
    """
    Drag source_node onto dest_node. These are tree.Node objects. Takes positions
    of these Nodes directly, so you don't have to calculate end enter them directly.
    """

    drag_node_to_node(
        source_node=source_node,
        destination_node=dest_node,
        button=button,
        check=check
    )


def dragWithTrajectory(  # pylint: disable=invalid-name
        fromXY,
        toXY,
        button=1,
        check=True,
        press_delay=0.5,
        mouse_delay=0.01
    ):
    """
    Synthesize a mouse press, drag (including move events), and release on the screen
    Please note, that on Wayland, this function works for drags only within a single window.
    On X this function works with global coords and equals dragWithTrajectoryGlobal
    """

    drag_with_trajectory(
        fromXY=fromXY,
        toXY=toXY,
        button=button,
        check=check,
        press_delay=press_delay,
        mouse_delay=mouse_delay
    )


def dragWithTrajectoryGlobal(fromXY, toXY, button=1):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over drag_with_trajectory_global
    """

    drag_with_trajectory_global(fromXY=fromXY, toXY=toXY, button=button)

###############################################
# End of backwards compatibility definitions. #
###############################################



# TODO Complete rewrite and improvement.
# TODO continue here



# Might split this to mouse and keyboard parts. TODO
def typeText(string):
    """
    Types the specified string, one character at a time.
    Please note, you may have to set a higher typing delay,
    if your machine misses/switches the characters typed.
    Needed sometimes on slow setups/VMs typing non-ASCII utf8 chars.
    """

    debug_log("typeText(string=%s)" % string)

    for char in string:
        pressKey(char)


keyNameAliases = {
    "enter": "Return",
    "esc": "Escape",
    "backspace": "BackSpace",
    "alt": "Alt_L",
    "control": "Control_L",
    "ctrl": "Control_L",
    "shift": "Shift_L",
    "del": "Delete",
    "ins": "Insert",
    "pageup": "Page_Up",
    "pagedown": "Page_Down",
    "win": "Super_L",
    "meta": "Super_L",
    "super": "Super_L",
    "tab": "Tab",
    "print": "Print",
    " ": "space",
    "\t": "Tab",
    "\n": "Return",
    "\b": "BackSpac"
}


def uniCharToKeySym(uniChar):
    """
    Use GDK to get the key symbol for a given unicode character.
    """

    debug_log("uniCharToKeySym(uniChar=%s)" % uniChar)

    i = ord(uniChar)
    keySym = Gdk.unicode_to_keyval(i)
    return keySym


def keyNameToKeySym(keyName):
    """
    Use GDK to get the key symbol for a key name.
    """

    debug_log("keyNameToKeySym(keyName=%s)" % keyName)

    keyName = keyNameAliases.get(keyName.lower(), keyName)
    keySym = Gdk.keyval_from_name(keyName)
    # various error 'codes' returned for non-recognized chars in versions of GTK3.X
    if keySym == 0xffffff or keySym == 0x0 or keySym is None:
        try:
            keySym = uniCharToKeySym(keyName)
        except Exception:  # not even valid utf-8 char
            try:  # Last attempt run at a keyName ('Meta_L', 'Dash' ...)
                keySym = getattr(Gdk, "KEY_" + keyName)
            except AttributeError:
                raise KeyError(keyName)
    return keySym


def keyNameToKeyCode(keyName):
    """
    Use GDK to get the keycode for a given keystring.

    Note that the keycode returned by this function is often incorrect when
    the requested keystring is obtained by holding down the Shift key.

    Generally you should use uniCharToKeySym() and should only need this
    function for nonprintable keys anyway.
    """

    debug_log("keyNameToKeyCode(keyName=%s)" % keyName)

    keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())
    entries = keymap.get_entries_for_keyval(Gdk.keyval_from_name(keyName))

    try:
        return entries[1][0].keycode
    except TypeError:
        pass


def pressKey(keyName, window_id=None):
    """
    Presses (and releases) the key specified by keyName.
    keyName is the English name of the key as seen on the keyboard. Ex: 'enter'
    Names are looked up in Gdk.KEY_ If they are not found there, they are
    looked up by uniCharToKeySym().
    """

    debug_log("pressKey(keyName=%s, window_id=%s)" % (keyName, str(window_id)))

    if keyName.lower() in ("esc", "escape", "enter", "return"):
        window_id = "" # when this would quit a window, release event would be doomed

    keySym = keyNameToKeySym(keyName)
    if SESSION_TYPE == "x11":
        registry.generateKeyboardEvent(keySym, None, KEY_SYM)
        doTypingDelay()

    else:
        ponytail_check_connection(window_id, input_source="keyboard")
        ponytail.generateKeysymEvent(keySym, delay=config.typingDelay/2)



def keyCombo(comboString):
    """
    Generates the appropriate keyboard events to simulate a user pressing the
    specified key combination.

    comboString is the representation of the key combo to be generated.
    e.g. '<Control><Alt>p' or '<Control><Shift>PageUp' or '<Control>q'
    """

    debug_log("keyCombo(comboString=%s)" % comboString)

    strings = []
    for s in comboString.split('<'):
        if s:
            for S in s.split('>'):
                if S:
                    S = keyNameAliases.get(S.lower(), S)
                    strings.append(S)

    for s in strings:
        if not hasattr(Gdk, s):
            if not hasattr(Gdk, "KEY_" + s):
                raise ValueError("Cannot find key '%s'" % s)

    modifiers = strings[:-1]
    finalKey = strings[-1]

    if SESSION_TYPE == "x11":
        for modifier in modifiers:
            code = keyNameToKeyCode(modifier)
            registry.generateKeyboardEvent(code, None, KEY_PRESS)

        code = keyNameToKeyCode(finalKey)
        registry.generateKeyboardEvent(code, None, KEY_PRESSRELEASE)

        for modifier in modifiers:
            code = keyNameToKeyCode(modifier)
            registry.generateKeyboardEvent(code, None, KEY_RELEASE)

    else:
        # always use monitor, window will often get closed
        # before final release i.e. with alt-f4 ctrl-q etc!
        ponytail_check_connection(input_source="keyboard", window_id="")

        for modifier in modifiers:
            code = keyNameToKeyCode(modifier)
            ponytail.generateKeycodePress(code)

        code = keyNameToKeyCode(finalKey)
        ponytail.generateKeycodeEvent(code)

        for modifier in modifiers:
            code = keyNameToKeyCode(modifier)
            ponytail.generateKeycodeRelease(code)

    doDelay()


def holdKey(keyName):
    """
    Press and hold the key specified by keyName.
    """

    debug_log("holdKey(keyName=%s)" % keyName)

    keyName = keyNameAliases.get(keyName.lower(), keyName)
    code = keyNameToKeyCode(keyName)

    if SESSION_TYPE == "x11":
        registry.generateKeyboardEvent(code, None, KEY_PRESS)

    else:
        ponytail_check_connection(input_source="keyboard")
        ponytail.generateKeycodePress(code)

    doDelay()


def releaseKey(keyName):
    """
    Releases the holded key specified by keyName.
    """

    debug_log("releaseKey(keyName=%s)" % keyName)

    keyName = keyNameAliases.get(keyName.lower(), keyName)
    code = keyNameToKeyCode(keyName)

    if SESSION_TYPE == "x11":
        registry.generateKeyboardEvent(code, None, KEY_RELEASE)

    else:
        ponytail_check_connection(input_source="keyboard")
        ponytail.generateKeycodeRelease(code)

    doDelay()
