"""Wrapper code to help when scripting gnome-panel

Author: David Malcolm <dmalcolm@redhat.com>"""

__author__ = 'David Malcolm <dmalcolm@redhat.com>'

from dogtail.tree import *
from dogtail.distro import packageDb
from dogtail.apps.categories import *
from dogtail.version import Version

class GnomePanel(Application):
    """Useful test hooks for GNOME panel testcases"""
    def __init__(self):
        Application.__init__(self, root.application("gnome-panel"))

        self.appVersion = packageDb.getVersion("gnome-panel")

        print "gnome-panel version %s"%self.appVersion

    def getApplicationsMenu(self):
        if self.appVersion>=Version([2,10.0]):
            # this works on FC5:
            return self.child(name = 'Applications', roleName = 'menu', recursive=True, debugName="Applications menu")
        else:
            # this makes it work on FC3:
            # assume that the first menu we find is the main menu:
            return self.findChild(predicate.GenericPredicate(roleName="menu"), recursive=True, debugName="Applications menu")

    def applications(self):
        """Generator of MenuItem for all menuitems representing applications under the Applications menu."""
        appMenu = self.getApplicationsMenu()

        return appMenu.findChildren(predicate.GenericPredicate(roleName="menu item"), recursive=True)
