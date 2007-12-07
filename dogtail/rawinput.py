# -*- coding: utf-8 -*-
"""
Handles raw input using AT-SPI event generation.

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
    doDelay()

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

def __buildKeyStringsDict(keySymsDict):
    syms = {}
    keyStringsDict = {}
    iter = keySymsDict.iteritems()
    while True:
        try:
            item = iter.next()
            """
            if item[1] in syms.keys():
                syms[item[1]].append(item[0])
                print item[1], syms[item[1]]
            else: 
                try: syms[item[1]] = [item[0]]
                except TypeError: pass
            """
            try:
                if not keyStringsDict.has_key(item[1]):
                    keyStringsDict[item[1]] = item[0]
            except TypeError: pass
        except StopIteration:
            return keyStringsDict

keySyms = gtk.keysyms.__dict__
keyStrings = __buildKeyStringsDict(keySyms)

keySymAliases = {
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
    i = ord(uniChar)
    keySym = gtk.gdk.unicode_to_keyval(i)
    return keySym

def pressKey(keyName):
    """
    Presses (and releases) the key specified by keyName.
    keyName is the English name of the key as seen on the keyboard. Ex: 'enter'
    Names are looked up in the keySyms dict. If they are not found there, 
    they are looked up by uniCharToKeySym().
    """
    try:
        keyName = keySymAliases.get(keyName.lower(), keyName)
        keySym = keySyms[keyName]
    except KeyError:
        try: keySym = uniCharToKeySym(keyName)
        except TypeError: raise KeyError, keyName
    registry.generateKeyboardEvent(keySym, None, KEY_SYM)
    doTypingDelay()

def gdkKeyStringToKeyCode(keyString):
    """
    Use GDK to get the keycode for a given keystring.
    """
    keymap = gtk.gdk.keymap_get_default()
    entries = keymap.get_entries_for_keyval( \
            gtk.gdk.keyval_from_name(keyString))
    try: return entries[0][0]
    except TypeError: pass

def xlibKeyStringToKeyCode(keyString):
    """
    Use xlib (via ctypes) to get the keycode for a given keystring.
    """
    def loadXlib():
        global xlib
        global dpy
        if xlib == None:
            xlib = ctypes.CDLL('libX11.so')
        if dpy == 0:
            dpy = ctypes.c_ulong(xlib.XOpenDisplay(None))

    def closeDpy():
        global dpy
        xlib.XCloseDisplay(dpy)
        dpy = 0

    def keyStringToKeySym(keyString, cleanup=False):
        loadXlib()
        string = ctypes.c_char_p(keyString)
        sym = ctypes.c_ulong(xlib.XStringToKeysym(string))
        if cleanup: closeDpy()
        return sym.value
        
    def keySymToKeyCode(keySym, cleanup=False):
        loadXlib()
        sym = ctypes.c_ulong(keySym)
        code = ctypes.c_byte(xlib.XKeysymToKeycode(dpy, sym))
        if cleanup: closeDpy()
        return code.value

    return keySymToKeyCode(keyStringToKeySym(keyString))

try:
    import ctypes
    xlib = None
    dpy = 0
    keyStringToKeyCode = xlibKeyStringToKeyCode
except ImportError:
    keyStringToKeyCode = gdkKeyStringToKeyCode

keyStringToKeyCode.__doc__ += """
    Note that the keycode returned by this function is often incorrect when
    the requested keystring is obtained by holding down the Shift key.
    
    Generally you should use uniCharToKeySym() and should only need this
    function for nonprintable keys anyway."""


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
                    S = keySymAliases.get(S.lower(), S)
                    strings.append(S)
    for s in strings:
        if not keySyms.has_key(s):
            raise ValueError, "Cannot find key %s" % s

    modifiers = strings[:-1]
    finalKey = strings[-1]

    for modifier in modifiers:
        code = keyStringToKeyCode(modifier)
        registry.generateKeyboardEvent(code, None, KEY_PRESS)

    code = keyStringToKeyCode(finalKey)
    registry.generateKeyboardEvent(code, None, KEY_PRESSRELEASE)

    for modifier in modifiers:
        code = keyStringToKeyCode(modifier)
        registry.generateKeyboardEvent(code, None, KEY_RELEASE)

    doDelay()

