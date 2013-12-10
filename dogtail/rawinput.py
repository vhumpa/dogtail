# -*- coding: utf-8 -*-
"""
Handles raw input using AT-SPI event generation.

Note: Think of keyvals as keysyms, and keynames as keystrings.

Authors: David Malcolm <dmalcolm@redhat.com>, Zack Cerza <zcerza@redhat.com>
"""

__author__ = """
David Malcolm <dmalcolm@redhat.com>,
Zack Cerza <zcerza@redhat.com>
"""
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk
from config import config
from utils import doDelay
from logging import debugLogger as logger
from pyatspi import Registry as registry
from pyatspi import (KEY_SYM, KEY_PRESS, KEY_PRESSRELEASE, KEY_RELEASE)
from exceptions import ValueError
from __builtin__ import unicode, unichr


def doTypingDelay():
    doDelay(config.typingDelay)


def checkCoordinates(x, y):
    if x < 0 or y < 0:
        raise ValueError(
            "Attempting to generate a mouse event at negative coordinates: (%s,%s)" % (x, y))


def click(x, y, button=1, check=True):
    """
    Synthesize a mouse button click at (x,y)
    """
    if check:
        checkCoordinates(x, y)
    logger.log("Mouse button %s click at (%s,%s)" % (button, x, y))
    registry.generateMouseEvent(x, y, 'b%sc' % button)
    doDelay(config.actionDelay)


def doubleClick(x, y, button=1, check=True):
    """
    Synthesize a mouse button double-click at (x,y)
    """
    if check:
        checkCoordinates(x, y)
    logger.log("Mouse button %s doubleclick at (%s,%s)" % (button, x, y))
    registry.generateMouseEvent(x, y, 'b%sd' % button)
    doDelay()


def press(x, y, button=1, check=True):
    """
    Synthesize a mouse button press at (x,y)
    """
    if check:
        checkCoordinates(x, y)
    logger.log("Mouse button %s press at (%s,%s)" % (button, x, y))
    registry.generateMouseEvent(x, y, 'b%sp' % button)
    doDelay()


def release(x, y, button=1, check=True):
    """
    Synthesize a mouse button release at (x,y)
    """
    if check:
        checkCoordinates(x, y)
    logger.log("Mouse button %s release at (%s,%s)" % (button, x, y))
    registry.generateMouseEvent(x, y, 'b%sr' % button)
    doDelay()


def absoluteMotion(x, y, mouseDelay=None, check=True):
    """
    Synthesize mouse absolute motion to (x,y)
    """
    if check:
        checkCoordinates(x, y)
    logger.log("Mouse absolute motion to (%s,%s)" % (x, y))
    registry.generateMouseEvent(x, y, 'abs')
    if mouseDelay:
        doDelay(mouseDelay)
    else:
        doDelay()


def relativeMotion(x, y, mouseDelay=None):
    logger.log("Mouse relative motion of (%s,%s)" % (x, y))
    registry.generateMouseEvent(x, y, 'rel')
    if mouseDelay:
        doDelay(mouseDelay)
    else:
        doDelay()


def drag(fromXY, toXY, button=1, check=True):
    """
    Synthesize a mouse press, drag, and release on the screen.
    """
    logger.log("Mouse button %s drag from %s to %s" % (button, fromXY, toXY))

    (x, y) = fromXY
    press(x, y, button, check)
    # doDelay()

    (x, y) = toXY
    absoluteMotion(x, y, check=check)
    doDelay()

    release(x, y, button, check)
    doDelay()


def typeText(string):
    """
    Types the specified string, one character at a time.
    Please note, you may have to set a higher typing delay,
    if your machine misses/switches the characters typed.
    Needed sometimes on slow setups/VMs typing non-ASCII utf8 chars.
    """
    if not isinstance(string, unicode):
        string = string.decode('utf-8')
    for char in string:
        pressKey(char)

keyNameAliases = {
    'enter': 'Return',
    'esc': 'Escape',
    'alt': 'Alt_L',
    'control': 'Control_L',
    'ctrl': 'Control_L',
    'shift': 'Shift_L',
    'del': 'Delete',
    'ins': 'Insert',
    'pageup': 'Page_Up',
    'pagedown': 'Page_Down',
    ' ': 'space',
    '\t': 'Tab',
    '\n': 'Return'
}


# TODO: Dead code
def keySymToUniChar(keySym):  # pragma: no cover
    i = Gdk.keyval_to_unicode(keySym)
    if i:
        UniChar = unichr(i)
    else:
        UniChar = ''
    return UniChar


def uniCharToKeySym(uniChar):
    # OK, if it's not actually unicode we can fix that, right?
    if not isinstance(uniChar, unicode):
        uniChar = unicode(uniChar, 'utf-8')
    i = ord(uniChar)
    keySym = Gdk.unicode_to_keyval(i)
    return keySym


# dead code
def keySymToKeyName(keySym):  # pragma: no cover
    return Gdk.keyval_name(keySym)


def keyNameToKeySym(keyName):
    keyName = keyNameAliases.get(keyName.lower(), keyName)
    keySym = Gdk.keyval_from_name(keyName)
    # various error 'codes' returned for non-recognized chars in versions of GTK3.X
    if keySym == 0xffffff or keySym == 0x0 or keySym is None:
        try:
            keySym = uniCharToKeySym(keyName)
        except: # not even valid utf-8 char
            try: # Last attempt run at a keyName ('Meta_L', 'Dash' ...)
                keySym = getattr(Gdk, 'KEY_' + keyName)
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
    keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())
    entries = keymap.get_entries_for_keyval(
        Gdk.keyval_from_name(keyName))
    try:
        return entries[1][0].keycode
    except TypeError:
        pass


def pressKey(keyName):
    """
    Presses (and releases) the key specified by keyName.
    keyName is the English name of the key as seen on the keyboard. Ex: 'enter'
    Names are looked up in Gdk.KEY_ If they are not found there, they are
    looked up by uniCharToKeySym().
    """
    keySym = keyNameToKeySym(keyName)
    registry.generateKeyboardEvent(keySym, None, KEY_SYM)
    doTypingDelay()


def keyCombo(comboString):
    """
    Generates the appropriate keyboard events to simulate a user pressing the
    specified key combination.

    comboString is the representation of the key combo to be generated.
    e.g. '<Control><Alt>p' or '<Control><Shift>PageUp' or '<Control>q'
    """
    strings = []
    for s in comboString.split('<'):
        if s:
            for S in s.split('>'):
                if S:
                    S = keyNameAliases.get(S.lower(), S)
                    strings.append(S)
    for s in strings:
        if not hasattr(Gdk, s):
            if not hasattr(Gdk, 'KEY_' + s):
                raise ValueError("Cannot find key %s" % s)
    modifiers = strings[:-1]
    finalKey = strings[-1]
    for modifier in modifiers:
        code = keyNameToKeyCode(modifier)
        registry.generateKeyboardEvent(code, None, KEY_PRESS)
    code = keyNameToKeyCode(finalKey)
    registry.generateKeyboardEvent(code, None, KEY_PRESSRELEASE)
    for modifier in modifiers:
        code = keyNameToKeyCode(modifier)
        registry.generateKeyboardEvent(code, None, KEY_RELEASE)
    doDelay()
