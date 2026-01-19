#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release. raw input.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=no-name-in-module
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


from dogtail.config import config
from dogtail.utils import do_delay

from dogtail.ponytail_helper import ponytail_helper
# To preserve API from dogtail-1.x lets provide ponytail here as well.
ponytail = ponytail_helper._ponytail_dbus_interface # pylint: disable=protected-access

from dogtail.logging import logging_class
LOGGING = logging_class.logger

SESSION_TYPE = "x11"
if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
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
    do_delay(float(config.typing_delay))


def click(x, y, button=1, check=True, window_id=None):
    """
    Synthesize a mouse button click at coordinates (x, y).
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # TODO remove and do it better.
    (_x, _y) = update_coords((x, y))

    # Check if the coordinates are not
    if check:
        check_coordinates(_x, _y)

    LOGGING.debug(f"Mouse button '{button}' click at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name=f"b{button}c")
    else:
        # ponytail_helper._ponytail_dbus_interface.disconnect()
        ponytail_helper.ponytail_check_connection(window_id)
        ponytail_interface = ponytail_helper.get_ponytail_interface()

        window_list = ponytail_interface.window_list
        debug_click = [(x["id"], x["has-focus"]) for x in window_list]
        LOGGING.debug(f"Ponytail click: '{debug_click}'")

        ponytail_interface.generateButtonEvent(button, _x, _y)

    do_delay(config.action_delay)


def point(x, y, check=True, window_id=None):
    """
    Synthesize a button point at (x,y)
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # TODO remove and do it better.
    (_x, _y) = update_coords((x, y))

    # Check if the coordinates are not
    if check:
        check_coordinates(_x, _y)

    LOGGING.debug(f"Mouse over at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name="abs")
    else:
        # ponytail_helper._ponytail_dbus_interface.disconnect()
        ponytail_helper.ponytail_check_connection(window_id)
        ponytail_interface = ponytail_helper.get_ponytail_interface()
        ponytail_interface.generateMotionEvent(_x, _y)

    do_delay(config.action_delay)


def double_click(x, y, button=1, check=True, window_id=None):
    """
    Synthesize a mouse button double-click at (x,y)
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # TODO remove and do it better.
    (_x, _y) = update_coords((x, y))

    # Check if the coordinates are not
    if check:
        check_coordinates(x, y)

    LOGGING.debug(f"Mouse button '{button}' double-click at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(x, y, name=f"b{button}d")
    else:
        # ponytail_helper._ponytail_dbus_interface.disconnect()
        ponytail_helper.ponytail_check_connection(window_id)
        ponytail_interface = ponytail_helper.get_ponytail_interface()
        ponytail_interface.generateButtonEvent(button, _x, _y)

        do_delay(config.double_click_delay)

        # Prevent executing release event on closed application
        ponytail_interface.generateButtonPress(button)
        if ponytail_interface.connected:
            ponytail_interface.generateButtonRelease(button)
        else: # not ponytail.connected:

            # ponytail_interface.disconnect()
            ponytail_interface.connectMonitor()

            ponytail_interface.generateButtonRelease(button)

    do_delay(config.action_delay)


def press(x, y, button=1, check=True, window_id=None, delay=None):
    """
    Synthesize a mouse button press at (x,y)
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # Check if user defined their own delay.
    if delay:
        delay_to_use = delay
    else:
        delay_to_use = config.default_delay

    # TODO remove and do it better.
    (_x, _y) = update_coords((x, y))

    if check:
        check_coordinates(_x, _y)

    LOGGING.debug(f"Mouse button '{button}' press at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name=f"b{button}p")

    else:
        # ponytail_helper._ponytail_dbus_interface.disconnect()
        ponytail_helper.ponytail_check_connection(window_id)
        ponytail_interface = ponytail_helper.get_ponytail_interface()
        ponytail_interface.generateMotionEvent(_x, _y)
        ponytail_interface.generateButtonPress(button)

    do_delay(delay_to_use)


def release(x, y, button=1, check=True, window_id=None):
    """
    Synthesize a mouse button release at (x,y)
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # TODO remove and do it better.
    (_x, _y) = update_coords((x, y))

    if check:
        check_coordinates(_x, _y)

    LOGGING.debug(f"Mouse button '{button}' release at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name=f"b{button}r")

    else:
        # ponytail_helper._ponytail_dbus_interface.disconnect()
        ponytail_helper.ponytail_check_connection(window_id)
        ponytail_interface = ponytail_helper.get_ponytail_interface()
        ponytail_interface.generateMotionEvent(_x, _y)

        do_delay(config.action_delay)

        ponytail_interface.generateButtonRelease(button)

    do_delay(config.action_delay)


def absolute_motion(x, y, mouse_delay=None, check=True, window_id=None):
    """
    Synthesize mouse absolute motion to (x,y)
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # Check if user defined their own delay.
    if mouse_delay:
        delay_to_use = mouse_delay
    else:
        delay_to_use = config.action_delay

    # TODO, remove and do it better.
    (_x, _y) = update_coords((x, y))

    if check:
        check_coordinates(_x, _y)

    LOGGING.debug(f"Mouse absolute motion at ({_x}, {_y})")

    if SESSION_TYPE == "x11":
        # TODO Newton if condition.
        Atspi.generate_mouse_event(_x, _y, name="abs")

    else:
        ponytail_helper.ponytail_check_connection(window_id)
        ponytail_interface = ponytail_helper.get_ponytail_interface()
        ponytail_interface.generateMotionEvent(_x, _y)

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

    LOGGING.debug(logging_class.get_func_params_and_values())

    # Check if user defined their own delay.
    if mouse_delay:
        delay_to_use = mouse_delay
    else:
        delay_to_use = config.action_delay

    if check:
        check_coordinates(source_x, source_y)
        check_coordinates(destination_x, destination_y)

    LOGGING.debug(f"Mouse absolute motion with trajectory at ({destination_x}, {destination_y})")

    difference_x = float(destination_x - source_x)
    difference_y = float(destination_y - source_y)
    max_length = max(abs(difference_x), abs(difference_y))

    if max_length == 0:
        return

    difference_x = difference_x / max_length
    difference_y = difference_y / max_length

    LOGGING.debug(f"Moving with difference of ({difference_x}, {difference_y})")

    act_x = float(source_x)
    act_y = float(source_y)

    for _ in range(0, int(max_length)):

        act_x += difference_x
        act_y += difference_y

        LOGGING.debug(f"Absolute motion with trajectory in progress ({act_x}, {act_y})")

        if mouse_delay:
            do_delay(mouse_delay)

        if SESSION_TYPE == "x11":
            # TODO Newton if condition.
            Atspi.generate_mouse_event(int(act_x), int(act_y), name="abs")

        else:
            ponytail_helper.ponytail_check_connection(window_id)
            ponytail_interface = ponytail_helper.get_ponytail_interface()
            ponytail_interface.generateMotionEvent(int(act_x), int(act_y))

    do_delay(delay_to_use)


def relative_motion(x, y, mouse_delay=None):
    """
    Synthesize a relative motion from actual position.
    Note: Does not check if the end coordinates are positive.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    LOGGING.debug(f"Mouse relative motion of ({x}, {y})")

    if SESSION_TYPE == "wayland":
        LOGGING.debug("Relative motion unavailable under wayland not available.")
        return

    # TODO Newton if condition.
    Atspi.generate_mouse_event(x, y, name="rel")

    if mouse_delay:
        do_delay(mouse_delay)
    else:
        do_delay(config.action_delay)


def drag(fromXY, toXY, button=1, check=True):  # pylint: disable=invalid-name
    """
    Synthesize a mouse press, drag, and release on the screen.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    LOGGING.debug(f"Mouse button '{button}' drag from '{fromXY}' to '{toXY}'")

    (_x, _y) = fromXY
    press(x=_x, y=_y, button=button, check=check)

    (_x, _y) = toXY
    absolute_motion(x=_x, y=_y, check=check)
    do_delay(config.action_delay)

    release(x=_x, y=_y, button=button, check=check)
    do_delay(config.action_delay)


def drag_node_to_node(source_node, destination_node, button=1, check=True):
    """
    Drag source_node onto dest_node. These are tree.Node objects. Takes positions
    of these Nodes directly, so you don't have to calculate end enter them directly.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    LOGGING.debug(f"Dragging from '{str(source_node)}' to '{str(destination_node)}'.")
    LOGGING.debug(f"Dragging using button '{button}' and check '{check}'")

    x = int(source_node.position[0] + source_node.size[0] / 2)
    y = int(source_node.position[1] + source_node.size[1] / 2)
    press(x, y, button, check, source_node.window_id)

    x = int(destination_node.position[0] + destination_node.size[0] / 2)
    y = int(destination_node.position[1] + destination_node.size[1] / 2)

    release(x, y, button, check, window_id=destination_node.window_id)
    do_delay(config.action_delay)


def drag_with_trajectory(  # pylint: disable=invalid-name
        fromXY,
        toXY,
        button=1,
        check=True,
        press_delay=0.2,
        mouse_delay=0.01
    ):
    """
    Synthesize a mouse press, drag (including move events), and release on the screen
    Please note, that on Wayland, this function works for drags only within a single window.
    On X this function works with global coords and equals dragWithTrajectoryGlobal
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # Check if user defined their own delay.
    if press_delay:
        delay_to_use = press_delay
    else:
        delay_to_use = config.default_delay

    LOGGING.debug(f"Dragging with trajectory from '{fromXY}' to '{toXY}'.")
    LOGGING.debug(f"Dragging using button '{button}' and check '{check}'")
    LOGGING.debug(f"Dragging using press delay '{delay_to_use}' and mouse_delay '{mouse_delay}'")

    (from_x, from_y) = fromXY
    press(x=from_x, y=from_y, button=button, check=check, delay=delay_to_use)

    (to_x, to_y) = toXY
    absolute_motion_with_trajectory(
        source_x=from_x,
        source_y=from_y,
        destination_x=to_x,
        destination_y=to_y,
        mouse_delay=mouse_delay,
        check=check
    )
    do_delay(config.action_delay)

    release(x=to_x, y=to_y, button=button, check=check)
    do_delay(config.action_delay)


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

    LOGGING.debug(logging_class.get_func_params_and_values())


    if SESSION_TYPE == "wayland":
        (from_x, from_y) = fromXY
        # ponytail_helper._ponytail_dbus_interface.disconnect()
        ponytail_helper.ponytail_check_connection(window_id="")
        ponytail_interface = ponytail_helper.get_ponytail_interface()

        ponytail_interface.generateMotionEvent(from_x, from_y)
        do_delay(config.action_delay)

        ponytail_interface.generateButtonPress(1)

        # We cannot do delay here or the behavior will change on long press.
        # do_delay(config.action_delay)

        (to_x, to_y) = toXY
        absolute_motion_with_trajectory(
            from_x,
            from_y,
            to_x,
            to_y,
            mouse_delay=0.01,
            window_id=""
        )

        ponytail_interface.generateMotionEvent(to_x, to_y)
        do_delay(config.action_delay)

        ponytail_interface.generateButtonRelease(1)
        do_delay(config.action_delay)

    else:
        drag_with_trajectory(fromXY, toXY, button)


# Section for Keyboard Events.

KEY_NAME_ALIASES = {
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
    "\b": "BackSpace"
}


def key_name_to_key_sym(key_name):
    """
    Use GDK to get the key symbol for a key name.

    :param key_name: Key Name
    :type key_name: str
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # Try to get the name from its alias.
    actual_key_name = KEY_NAME_ALIASES.get(key_name.lower(), key_name)
    LOGGING.debug(f"Key name after possible alias used '{actual_key_name}'.")

    # Get name vale from Gdk.keyval_from_name.
    actual_key_sym = Gdk.keyval_from_name(actual_key_name)
    LOGGING.debug(f"Key symbol value after Gdk.keyval_from_name '{actual_key_sym}'.")

    # If an error value is detected.
    if actual_key_sym in (0xffffff, 0x0, None):
        LOGGING.debug("Error value was detected '0xffffff, 0x0, None'.")
        try:

            LOGGING.debug("Attempt to get key value from Unicode representation of the key.")
            # Unicode code from a given character.
            unicode_key_value = ord(actual_key_name)
            actual_key_sym = Gdk.unicode_to_keyval(unicode_key_value)
            LOGGING.debug(f"Key symbol value from Gdk.unicode_to_keyval '{actual_key_sym}'.")

        # Not valid utf-8 character.
        except Exception as error :
            LOGGING.debug(f"Not valid character '{error}'.")

            try:

                LOGGING.debug("Attempt to match key name with Gdk.KEY_<key_name>.")
                actual_key_sym = getattr(Gdk, f"KEY_{actual_key_sym}")

            except AttributeError as attribute_error:
                # Caught Attribute Error is in reality a Key Error of user.
                raise KeyError(key_name) from attribute_error

    return actual_key_sym


def key_name_to_key_code(key_name):
    """
    Use GDK to get the keycode for a given key string.

    Note that the keycode returned by this function is often incorrect when
    the requested key string is obtained by holding down the Shift key.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    # Get Display.
    display = Gdk.Display().get_default()

    # Get Key Map
    key_map = Gdk.Keymap().get_for_display(display)

    # Get Key value.
    key_symbol_value = key_name_to_key_sym(key_name)
    entries = key_map.get_entries_for_keyval(key_symbol_value)

    try:
        return entries[1][0].keycode
    except TypeError:
        return key_name


def press_key(key_name, window_id=None):
    """
    Presses (and releases) the key specified by key_name.
    The key_name is the English name of the key as seen on the keyboard. Ex: 'enter'
    Names are looked up in Gdk.KEY_ If they are not found there, they are
    looked up by Gdk.unicode_to_keyval(key_name).
    """

    LOGGING.debug(logging_class.get_func_params_and_values())


    if key_name.lower() in ("esc", "escape", "enter", "return"):
        # When this would quit a window, release event would be doomed.
        window_id = ""

    key_symbol_value = key_name_to_key_sym(key_name)

    if SESSION_TYPE == "x11":
        Atspi.generate_keyboard_event(key_symbol_value, None, Atspi.KeySynthType.SYM)
        do_delay(float(config.typing_delay))

    else:
        ponytail_helper.ponytail_check_connection(window_id, input_source="keyboard")
        ponytail_interface = ponytail_helper.get_ponytail_interface()

        use_delay = float(config.typing_delay)
        ponytail_interface.generateKeysymEvent(key_symbol_value, delay=use_delay)


def hold_key(key_name):
    """
    Press and hold the key specified by key_name.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())


    key_code = key_name_to_key_code(key_name)

    if SESSION_TYPE == "x11":
        Atspi.generate_keyboard_event(key_code, None, Atspi.KeySynthType.PRESS)
        do_delay(float(config.typing_delay))

    else:
        ponytail_helper.ponytail_check_connection(input_source="keyboard")
        ponytail_interface = ponytail_helper.get_ponytail_interface()
        ponytail_interface.generateKeycodePress(key_code)

    do_delay(config.action_delay)


def release_key(key_name):
    """
    Releases the held key specified by keyName.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    LOGGING.debug(f"Attempting to release key of name '{key_name}'.")

    key_code = key_name_to_key_code(key_name)

    if SESSION_TYPE == "x11":
        Atspi.generate_keyboard_event(key_code, None, Atspi.KeySynthType.RELEASE)
        do_delay(float(config.typing_delay))

    else:
        ponytail_helper.ponytail_check_connection(input_source="keyboard")
        ponytail_interface = ponytail_helper.get_ponytail_interface()
        ponytail_interface.generateKeycodePress(key_code)

    do_delay(config.action_delay)


def type_text(string):
    """
    Types the specified string, one character at a time.
    Please note, you may have to set a higher typing delay,
    if your machine misses/switches the characters typed.
    Needed sometimes on slow setups/VMs typing non-ASCII utf8 chars.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    for character in string:
        press_key(character)


def key_combo(combo_string):
    """
    Generates the appropriate keyboard events to simulate a user pressing the
    specified key combination.

    The combo_string is the representation of the key combo to be generated.
    e.g. '<Control><Alt>p' or '<Control><Shift>PageUp' or '<Control>q'

    The combo string does not need to have a final key. It can also be used as.
    '<Control><Alt><P>' or '<Control><Shift><PageUp>' or '<Control><Q>' which might be
    more readable in some situations.
    """

    LOGGING.debug(logging_class.get_func_params_and_values())

    keys_to_press = []
    # Remove left side lesser than sign.
    for key_partial_split in combo_string.split("<"):
        if key_partial_split:
            # Remove right side bigger than sign.
            for key_full_split in key_partial_split.split(">"):
                if key_full_split:
                    possible_alias_use = KEY_NAME_ALIASES.get(
                        key_full_split.lower(), # key
                        key_full_split # default
                    )
                    keys_to_press.append(possible_alias_use)

    # Check that the keys to be pressed are defined.
    for key_name in keys_to_press:
        if not hasattr(Gdk, key_name):
            if not hasattr(Gdk, f"KEY_{key_name}"):
                raise ValueError(f"Cannot find key '{key_name}'")

    # Get all keys leading up to the final key.
    modifiers = keys_to_press[:-1]

    # Get the final key to press.
    final_key = keys_to_press[-1]

    if SESSION_TYPE == "x11":
        # First press all modifiers leading up to the final key.
        for modifier in modifiers:
            # TODO figure out how to tell if Newton is to be used.
            key_code = key_name_to_key_code(modifier)
            Atspi.generate_keyboard_event(key_code, None, Atspi.KeySynthType.PRESS)

        # TODO figure out how to tell if Newton is to be used.
        final_key_code = key_name_to_key_code(final_key)
        Atspi.generate_keyboard_event(final_key_code, None, Atspi.KeySynthType.PRESSRELEASE)

        # Than release all modifiers after the final key was pressed and released.
        for modifier in modifiers:
            # TODO figure out how to tell if Newton is to be used.
            key_code = key_name_to_key_code(modifier)
            Atspi.generate_keyboard_event(key_code, None, Atspi.KeySynthType.RELEASE)

    else:
        #Always use monitor, window will often get closed
        # before final release i.e. with Alt-F4, Ctrl-Q etc!

        ponytail_helper.ponytail_check_connection(window_id="", input_source="keyboard")
        ponytail_interface = ponytail_helper.get_ponytail_interface()

        # First press all modifiers leading up to the final key.
        for modifier in modifiers:
            key_code = key_name_to_key_code(modifier)
            ponytail_interface.generateKeycodePress(key_code)

        key_code = key_name_to_key_code(final_key)
        ponytail_interface.generateKeycodeEvent(key_code)

        # Than release all modifiers after the final key was pressed and released.
        for modifier in modifiers:
            key_code = key_name_to_key_code(modifier)
            ponytail_interface.generateKeycodeRelease(key_code)

    do_delay(config.action_delay)


########################################
# Backwards compatibility definitions. #
########################################
def doubleClick(x, y, button=1, check=True, window_id=None):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over double_click.
    """

    double_click(x=x, y=y, button=button, check=check, window_id=window_id)


def doTypingDelay():  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over do_typing_delay.
    """

    do_typing_delay()


def absoluteMotion(x, y, mouseDelay=None, check=True, window_id=None):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over absolute_motion.
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
    Backwards compatibility wrapper over absolute_motion_with_trajectory.
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
    Backwards compatibility wrapper over relative_motion.
    """

    relative_motion(x=x, y=y, mouse_delay=mouseDelay)


def dragNodeToNode(source_node, dest_node, button=1, check=True):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over drag_node_to_node.
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
    Backwards compatibility wrapper over drag_with_trajectory.
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


def pressKey(keyName, window_id=None):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over press_key.
    """

    press_key(key_name=keyName, window_id=window_id)


def typeText(string):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over type_text.
    """

    type_text(string=string)


def keyNameToKeyCode(keyName):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over key_name_to_key_code.
    """

    return key_name_to_key_code(key_name=keyName)


def holdKey(keyName):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over hold_key.
    """

    hold_key(key_name=keyName)


def releaseKey(keyName):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over release_key.
    """

    release_key(key_name=keyName)


def keyCombo(comboString):  # pylint: disable=invalid-name
    """
    Backwards compatibility wrapper over key_combo.
    """

    key_combo(combo_string=comboString)


# To keep backwards compatibility and allow users to import doDelay from here.
def doDelay(delay=None):  # pylint: disable=invalid-name
    """
    Do Delay.
    """

    do_delay(delay=delay)
###############################################
# End of backwards compatibility definitions. #
###############################################
