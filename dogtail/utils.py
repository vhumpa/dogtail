# -*- coding: utf-8 -*-
"""
Various utilities

Authors: Ed Rousseau <rousseau@redhat.com>, Zack Cerza <zcerza@redhat.com, David Malcolm <dmalcolm@redhat.com>
"""

__author__ = """Ed Rousseau <rousseau@redhat.com>,
Zack Cerza <zcerza@redhat.com,
David Malcolm <dmalcolm@redhat.com>
"""

import os
import sys
import subprocess
import re
import cairo
from gi.repository import Gtk
from config import config
from time import sleep
from logging import debugLogger as logger
from logging import TimeStamp
from errors import DependencyNotFoundError

def screenshot(file = 'screenshot.png', timeStamp = True):
    """
    This function wraps the ImageMagick import command to take a screenshot.

    The file argument may be specified as 'foo', 'foo.png', or using any other
    extension that ImageMagick supports. PNG is the default.

    By default, screenshot filenames are in the format of foo_YYYYMMDD-hhmmss.png .
    The timeStamp argument may be set to False to name the file foo.png.
    """
    if not isinstance(timeStamp, bool):
        raise TypeError, "timeStampt must be True or False"
    # config is supposed to create this for us. If it's not there, bail.
    assert os.path.isdir(config.scratchDir)

    baseName = ''.join(file.split('.')[0:-1])
    fileExt = file.split('.')[-1].lower()
    if not baseName:
        baseName = file
        fileExt = 'png'

    if timeStamp:
        ts = TimeStamp()
        newFile = ts.fileStamp(baseName) + '.' + fileExt
        path = config.scratchDir + newFile
    else:
        newFile = baseName + '.' + fileExt
        path = config.scratchDir + newFile

    from gi.repository import Gdk
    from gi.repository import GObject
    rootWindow = Gdk.get_default_root_window()
    geometry = rootWindow.get_geometry()
    pixbuf = GdkPixbuf.Pixbuf(GdkPixbuf.Colorspace.RGB, False, 8, geometry[2], \
            geometry[3])
    GdkPixbuf.Pixbuf.get_from_drawable(pixbuf, rootWindow, \
            rootWindow.get_colormap(), 0, 0, 0, 0, geometry[2], geometry[3])
    # GdkPixbuf.Pixbuf.save() needs 'jpeg' and not 'jpg'
    if fileExt == 'jpg': fileExt = 'jpeg'
    try: pixbuf.save(path, fileExt)
    except GObject.GError:
        raise ValueError, "Failed to save screenshot in %s format" % fileExt
    assert os.path.exists(path)
    logger.log("Screenshot taken: " + path)
    return path

def run(string, timeout=config.runTimeout, interval=config.runInterval, desktop=None, dumb=False, appName=''):
    """
    Runs an application. [For simple command execution such as 'rm *', use os.popen() or os.system()]
    If dumb is omitted or is False, polls at interval seconds until the application is finished starting, or until timeout is reached.
    If dumb is True, returns when timeout is reached.
    """
    if not desktop: from tree import root as desktop
    args = string.split()
    name = args[0]
    os.environ['GTK_MODULES'] = 'gail:atk-bridge'
    pid = subprocess.Popen(args, env = os.environ).pid

    if not appName:
        appName=args[0]

    if dumb:
        # We're starting a non-AT-SPI-aware application. Disable startup detection.
        doDelay(timeout)
    else:
        # Startup detection code
        # The timing here is not totally precise, but it's good enough for now.
        time = 0
        while time < timeout:
            time = time + interval
            try:
                for child in desktop.children[::-1]:
                    if child.name == appName:
                        for grandchild in child.children:
                            if grandchild.roleName == 'frame':
                                from procedural import focus
                                focus.application.node = child
                                doDelay(interval)
                                return pid
            except AttributeError: pass
            doDelay(interval)
    return pid

def doDelay(delay=None):
    """
    Utility function to insert a delay (with logging and a configurable
    default delay)
    """
    if delay is None:
        delay = config.defaultDelay
    if config.debugSleep:
        logger.log("sleeping for %f" % delay)
    sleep(delay)

class Highlight (Gtk.Window):

    def __init__(self, x, y, w, h):
        super(Highlight, self).__init__()
        self.set_decorated(False)
        self.set_has_resize_grip(False)
        self.set_default_size(w, h)
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual is not None and self.screen.is_composited():
            self.set_visual(self.visual)
        self.set_app_paintable(True)
        self.connect("draw", self.area_draw)
        self.show_all()
        self.move(x,y)

    def area_draw(self, widget, cr):
        cr.set_source_rgba(.0, .0, .0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.set_source_rgb(0.9, 0.1, 0.1)
        cr.set_line_width(6)
        cr.rectangle(0, 0, self.get_size()[0], self.get_size()[1])
        cr.stroke()

class Blinker:
    INTERVAL_MS = 1000
    def __init__(self, x, y, w, h):
        from gi.repository import GObject
        from gi.repository import Gdk
        self.highlight_window = Highlight(x, y, w, h)
        if self.highlight_window.screen.is_composited() is not False:
            self.timeout_handler_id = GObject.timeout_add (Blinker.INTERVAL_MS, self.destroyHighlight)
        else:
            self.highlight_window.destroy()

    def destroyHighlight(self):
        self.highlight_window.destroy()
        return False

a11yGConfKey = '/desktop/gnome/interface/accessibility'

def isA11yEnabled():
    """
    Checks if accessibility is enabled via GConf.
    """
    from gi.repository import GConf
    gconfEnabled = GConf.Client.get_default().get_bool(a11yGConfKey)
    if os.environ.get('GTK_MODULES','').find('gail:atk-bridge') == -1:
        envEnabled = False
    else: envEnabled = True
    return (gconfEnabled or envEnabled)

def bailBecauseA11yIsDisabled():
    if sys.argv[0].endswith("pydoc"): return
    try:
        if file("/proc/%s/cmdline" % os.getpid()).read().find('epydoc') != -1:
            return
    except: pass
    logger.log("Dogtail requires that Assistive Technology support be enabled. Aborting...")
    sys.exit(1)

def enableA11y():
    """
    Enables accessibility via GConf.
    """
    from gi.repository import GConf
    return GConf.Client.get_default().set_bool(a11yGConfKey, True)

def checkForA11y():
    """
    Checks if accessibility is enabled, and halts execution if it is not.
    """
    if not isA11yEnabled(): bailBecauseA11yIsDisabled()

def checkForA11yInteractively():
    """
    Checks if accessibility is enabled, and presents a dialog prompting the
    user if it should be enabled if it is not already, then halts execution.
    """
    if isA11yEnabled(): return
    from gi.repository import Gtk
    dialog = Gtk.Dialog('Enable Assistive Technology Support?',
                     None,
                     Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                     (Gtk.STOCK_QUIT, Gtk.ResponseType.CLOSE,
                         "_Enable", Gtk.ResponseType.ACCEPT))
    question = """Dogtail requires that Assistive Technology Support be enabled for it to function. Would you like to enable Assistive Technology support now?

Note that you will have to log out for the change to fully take effect.
    """.strip()
    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    questionLabel = Gtk.Label(label=question)
    questionLabel.set_line_wrap(True)
    dialog.vbox.pack_start(questionLabel, True, True, 0)
    dialog.show_all()
    result = dialog.run()
    if result == Gtk.ResponseType.ACCEPT:
        logger.log("Enabling accessibility...")
        enableA11y()
    elif result == Gtk.ResponseType.CLOSE:
       bailBecauseA11yIsDisabled()
    dialog.destroy()

