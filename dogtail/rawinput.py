# -*- coding: utf-8 -*-
"""
Handles raw input using AT-SPI event generation.

Authors: David Malcolm <dmalcolm@redhat.com>, Zack Cerza <zcerza@redhat.com>
"""

__author__ = """
David Malcolm <dmalcolm@redhat.com>,
Zack Cerza <zcerza@redhat.com>
"""

import atspi
import gtk.keysyms
import gtk.gdk
from config import config
from utils import doDelay
from logging import debugLogger as logger
ev = atspi.EventGenerator()

def doTypingDelay():
    doDelay(config.typingDelay)

def click (x, y, button = 1):
    """
    Synthesize a mouse button click at (x,y)
    """
    logger.log("Mouse button %s click at (%s,%s)"%(button,x,y))
    ev.click(x, y, button)
    doDelay()

def doubleClick (x, y, button = 1):
    """
    Synthesize a mouse button double-click at (x,y)
    """
    logger.log("Mouse button %s doubleclick at (%s,%s)"%(button,x,y))
    ev.doubleClick(x,y,button)
    doDelay()

def press (x, y, button = 1):
    """
    Synthesize a mouse button press at (x,y)
    """
    logger.log("Mouse button %s press at (%s,%s)"%(button,x,y))
    ev.press(x,y, button)
    doDelay()

def release (x, y, button = 1):
    """
    Synthesize a mouse button release at (x,y)
    """
    logger.log("Mouse button %s release at (%s,%s)"%(button,x,y))
    ev.release(x,y,button)
    doDelay()

def absoluteMotion (x, y):
    """
    Synthesize mouse absolute motion to (x,y)
    """
    logger.log("Mouse absolute motion to (%s,%s)"%(x,y))
    ev.absoluteMotion(x,y)
    doDelay()

def relativeMotion (x, y):
    logger.log("Mouse relative motion of (%s,%s)"%(x,y))
    ev.relativeMotion(x,y)
    doDelay()

def drag(fromXY, toXY, button = 1):
    """
    Synthesize a mouse press, drag, and release on the screen.
    Wraps atspi.EventGenerator.drag, but with logging and delays.
    """
    logger.log("Mouse button %s drag from %s to %s"%(button, fromXY, toXY))

    # A direct call to ev.drag doesn't work, delays seem to be needed
    # for nautilus icon view to work, at least:

    (x,y) = fromXY
    ev.press (x, y, button)
    #doDelay()

    (x,y) = toXY
    ev.absoluteMotion(x,y)
    doDelay()

    ev.release (x, y, button)
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
    Names are looked up in the keySyms dict.
    """
    #keyName = keySymAliases.get(keyName.lower(), keyName)
    #keySym = keySyms[keyName]
    keySym = uniCharToKeySym(keyName)
    ev.generateKeyboardEvent(keySym, "", atspi.SPI_KEY_SYM)
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
                    S = keySymAliases.get(S.lower(), S)
                    strings.append(S)
    for s in strings:
        if not keySyms.has_key(s):
            raise ValueError, "Cannot find key %s" % s

    ev.generateKeyCombo(strings)
    doDelay()


