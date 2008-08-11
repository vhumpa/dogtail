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

import gtk.keysyms
import gtk.gdk
from config import config
from utils import doDelay
from logging import debugLogger as logger
from pyatspi import Registry as registry
from pyatspi import (KEY_SYM, KEY_PRESS, KEY_PRESSRELEASE, KEY_RELEASE)

def doTypingDelay():
    doDelay(config.typingDelay)

def click (x, y, button = 1):
    """
    Synthesize a mouse button click at (x,y)
    """
    logger.log("Mouse button %s click at (%s,%s)"%(button,x,y))
    registry.generateMouseEvent(x, y, 'b%sc' % button)
    doDelay(config.actionDelay)

def doubleClick (x, y, button = 1):
    """
    Synthesize a mouse button double-click at (x,y)
    """
    logger.log("Mouse button %s doubleclick at (%s,%s)"%(button,x,y))
    registry.generateMouseEvent(x,y, 'b%sd' % button)
    doDelay()

def press (x, y, button = 1):
    """
    Synthesize a mouse button press at (x,y)
    """
    logger.log("Mouse button %s press at (%s,%s)"%(button,x,y))
    registry.generateMouseEvent(x,y, 'b%sp' % button)
    doDelay()

def release (x, y, button = 1):
    """
    Synthesize a mouse button release at (x,y)
    """
    logger.log("Mouse button %s release at (%s,%s)"%(button,x,y))
    registry.generateMouseEvent(x,y, 'b%sr' % button)
    doDelay()

def absoluteMotion (x, y):
    """
    Synthesize mouse absolute motion to (x,y)
    """
    logger.log("Mouse absolute motion to (%s,%s)"%(x,y))
    registry.generateMouseEvent(x,y, 'abs')
    doDelay()

def relativeMotion (x, y):
    logger.log("Mouse relative motion of (%s,%s)"%(x,y))
    registry.generateMouseEvent(x,y, 'rel')
    doDelay()

def drag(fromXY, toXY, button = 1):
    """
    Synthesize a mouse press, drag, and release on the screen.
    """
    logger.log("Mouse button %s drag from %s to %s"%(button, fromXY, toXY))

    (x,y) = fromXY
    press (x, y, button)
    #doDelay()

    (x,y) = toXY
    absoluteMotion(x,y)
    doDelay()

    release (x, y, button)
    doDelay()

def typeText(string):
    """
    Types the specified string, one character at a time.
    """
    if not isinstance(string, unicode):
        string = string.decode('utf-8')
    for char in string:
        pressKey(char)

keyNameAliases = {
    'enter' : 'Return',
    'esc' : 'Escape',
    'alt' : 'Alt_L',
    'control' : 'Control_L',
    'ctrl' : 'Control_L',
    'shift' : 'Shift_L',
    'del' : 'Delete',
    'ins' : 'Insert',
    'pageup' : 'Page_Up',
    'pagedown' : 'Page_Down',
    ' ' : 'space',
    '\t' : 'Tab',
    '\n' : 'Return'
}

def keySymToUniChar(keySym):
    i = gtk.gdk.keyval_to_unicode(keySym)
    if i: UniChar = unichr(i)
    else: UniChar = ''
    return UniChar

def uniCharToKeySym(uniChar):
    # OK, if it's not actually unicode we can fix that, right?
    if not isinstance(uniChar, unicode): uniChar = unicode(uniChar)
    i = ord(uniChar)
    keySym = gtk.gdk.unicode_to_keyval(i)
    return keySym

def keySymToKeyName(keySym):
    return gtk.gdk.keyval_name(keySym)

def keyNameToKeySym(keyName):
    try:
        keyName = keyNameAliases.get(keyName.lower(), keyName)
        keySym = gtk.gdk.keyval_from_name(keyName)
        if not keySym: keySym = getattr(gtk.keysyms, keyName)
    except AttributeError:
        try: keySym = uniCharToKeySym(keyName)
        except TypeError: raise KeyError, keyName
    return keySym

def keyNameToKeyCode(keyName):
    """
    Use GDK to get the keycode for a given keystring.

    Note that the keycode returned by this function is often incorrect when
    the requested keystring is obtained by holding down the Shift key.
    
    Generally you should use uniCharToKeySym() and should only need this
    function for nonprintable keys anyway.
    """
    keymap = gtk.gdk.keymap_get_default()
    entries = keymap.get_entries_for_keyval( \
            gtk.gdk.keyval_from_name(keyName))
    try: return entries[0][0]
    except TypeError: pass

def pressKey(keyName):
    """
    Presses (and releases) the key specified by keyName.
    keyName is the English name of the key as seen on the keyboard. Ex: 'enter'
    Names are looked up in gtk.keysyms. If they are not found there, they are
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
        if not hasattr(gtk.keysyms, s):
            raise ValueError, "Cannot find key %s" % s

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

