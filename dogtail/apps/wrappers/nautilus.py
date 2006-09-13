"""Wrapper code to help when scripting Nautilus

Author: David Malcolm <dmalcolm@redhat.com>"""

__author__ = 'David Malcolm <dmalcolm@redhat.com>'

from dogtail.tree import *
from dogtail.distro import packageDb

import os

class IsAnIcon(predicate.Predicate):
    """Search subclass that looks for icons"""
    def satisfiedByNode(self, node):
        return node.roleName=='icon'

    def describeSearchResult(self):
        return 'icon'

class NautilusApp(Application):
    """Utility wrapper for Nautilus"""

    def __init__ (self):
        Application.__init__(self, root.application("nautilus"))

        self.nautiVersion = packageDb.getVersion("nautilus")
        print "Nautilus version %s"%self.nautiVersion

        try:
            self.gnomevfsVersion = packageDb.getVersion("gnome-vfs2")
            print "GnomeVFS version %s"%self.gnomevfsVersion
        except: pass # handle undetected gnomevfs version; probably named differently on different distros

    def openPath (self, path):
        """
        Open a Nautilus spatial window for the given path (not a URL).

        Returns a Window instance
        """
        os.system('nautilus %s'%os.path.abspath(path))

        return NautilusWindow(self.window(windowName=os.path.basename(path)))

class NautilusWindow(Window):
    def iconView (self):
        return self.child("Content View").child("Icon View")
