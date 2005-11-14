#!/usr/bin/env python
"""
Handles raw input using AT-SPI event generation.

Authors: David Malcolm <dmalcolm@redhat.com>, Zack Cerza <zcerza@redhat.com>
"""

__author__ = """
David Malcolm <dmalcolm@redhat.com>,
Zack Cerza <zcerza@redhat.com>
"""

import atspi
from utils import doDelay
from logging import debugLogger as logger

def click (x, y, button = 1):
	"""
	Synthesize a mouse button click at (x,y)
	"""
	logger.log("Mouse button %s click at (%s,%s)"%(button,x,y))
	ev = atspi.EventGenerator()
	ev.click(x, y, button)
	doDelay()
	
def doubleClick (x, y, button = 1):
	"""
	Synthesize a mouse button double-click at (x,y)
	"""
	logger.log("Mouse button %s doubleclick at (%s,%s)"%(button,x,y))
	ev = atspi.EventGenerator()
	ev.doubleClick(x,y,button)
	doDelay()

def press (x, y, button = 1):
	"""
	Synthesize a mouse button press at (x,y)
	"""
	logger.log("Mouse button %s press at (%s,%s)"%(button,x,y))
	ev = atspi.EventGenerator()
	ev.press(x,y, button)
	doDelay()
	
def release (x, y, button = 1):
	"""
	Synthesize a mouse button release at (x,y)
	"""
	logger.log("Mouse button %s release at (%s,%s)"%(button,x,y))
	ev = atspi.EventGenerator()
	ev.release(x,y,button)
	doDelay()

def absoluteMotion (x, y):
	"""
	Synthesize mouse absolute motion to (x,y)
	"""
	logger.log("Mouse absolute motion to (%s,%s)"%(x,y))
	ev = atspi.EventGenerator()
	ev.absoluteMotion(x,y)
	doDelay()

def relativeMotion (x, y):
	logger.log("Mouse relative motion of (%s,%s)"%(x,y))
	ev = atspi.EventGenerator()
	ev.relativeMotion(x,y)
	doDelay()

def drag(fromXY, toXY, button = 1):
	"""
	Synthesize a mouse press, drag, and release on the screen.
	Wraps atspi.EventGenerator.drag, but with logging and delays.
	"""
	logger.log("Mouse button %s drag from %s to %s"%(button, fromXY, toXY))
	ev = atspi.EventGenerator()

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
	ev = atspi.EventGenerator()
	ev.injectKeyboardString(string)

keySyms = {
	'enter' : 0xff0d,
	'esc' : 0xff1b,
	'space' : 0x20
}

def pressKey(keyName):
	"""
	Presses (and releases) the key specified by keyName.
	keyName is the English name of the key as seen on the keyboard. Ex: 'enter'
	Names are looked up in the keySyms dict.
	"""
	ev = atspi.EventGenerator()
	keySym = keySyms[keyName.lower()]
	ev.generateKeyboardEvent(keySym, "", atspi.SPI_KEY_SYM)

